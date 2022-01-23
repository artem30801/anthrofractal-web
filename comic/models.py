from django.db import models
from django.utils import timezone
# from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from tagulous.models import TagField, TagModel
import tagulous.models

import datetime
import uuid


class PanelTag(TagModel):
    class TagMeta:
        force_lowercase = True
        space_delimiter = False
        blank = True

    def get_absolute_url(self):
        return reverse('comic-search-tag', kwargs={'slug': self.slug})

    def fullname(self):
        return f"Tag - {self.name}"


class Numbered(models.Model):
    objects = models.Manager()
    number = models.PositiveIntegerField(unique=True, default=0,
                                         help_text="Leave it as '0' to be determined automatically "
                                                   "or specify any number (must be unique)")

    class Meta:
        ordering = ['number']
        abstract = True

    @property
    def next_number(self):
        return self.number + 1

    @property
    def previous_number(self):
        return self.number - 1

    @classmethod
    def first_number(cls):
        return 1

    @classmethod
    def last_number(cls):
        max_number = cls.objects.aggregate(models.Max('number'))['number__max']
        return max_number

    @classmethod
    def _last_number_private(cls):
        return cls.last_number()

    def save(self, *args, **kwargs):
        if self.number == 0:
            last_number = self._last_number_private()
            if not last_number:
                self.number = 1
            else:
                self.number = last_number + 1

        super().save(*args, **kwargs)


class Page(Numbered):
    title = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Page №{self.number}: {self.title or 'NO TITLE'}"

    def get_absolute_url(self):
        first_panel = self.panels.order_by('number').first()
        return reverse('comic-panel', kwargs={'number': first_panel.number})

    @property
    def fullname(self):
        return f"Page {self.number:02d} - {self.title}"

    @classmethod
    def get_default_pk(cls):
        max_number_page = cls.objects.order_by('-number').first()
        if max_number_page is not None:
            return max_number_page.pk

        return 0

    def panel_count(self):
        return self.panels.all().count()


class ComicPanel(Numbered):
    published = models.DateTimeField('date published', default=timezone.now)
    title = models.CharField(max_length=200, blank=True)
    alt = models.CharField(max_length=100, blank=True,
                           verbose_name="Alt text",
                           help_text="Replaces image if it can't be loaded; "
                                     "can be used to hide secrets in HTML",
                           )
    tags = TagField(to=PanelTag, blank=True)
    page = models.ForeignKey(Page, related_name='panels',
                             on_delete=models.CASCADE, default=Page.get_default_pk)

    image = models.ImageField(upload_to='panels')

    def __str__(self):
        return f"Panel {self.number:02d} - {self.title}"

    def get_absolute_url(self):
        return reverse('comic-panel', kwargs={'number': self.number})

    @property
    def fullname(self):
        # return f"{self.number}. {self.title}"
        return f"{self.page.number:02d}.{self.number_in_page():02d} - {self.title}"

    @property
    def pagename(self):
        return f"{self.number_in_page():02d} - {self.title}"

    def number_in_page(self):
        index = self.__class__.objects.filter(page=self.page, number__lt=self.number).count()
        return index + 1

    @classmethod
    def last_number(cls):
        max_number = cls.objects.filter(published__lte=timezone.now()).aggregate(models.Max('number'))['number__max']
        return max_number

    @classmethod
    def _last_number_private(cls):
        return super()._last_number_private()

    @classmethod
    def next_publish(cls):
        next_panel = cls.objects.filter(published__gt=timezone.now()).first()
        if next_panel is None:
            # no panels in 'backlog'
            latest_panel = cls.objects.last()
            next_publish = latest_panel.published + datetime.timedelta(days=7)
        else:
            next_publish = next_panel.published

        return next_publish

    def is_published(self) -> bool:
        return self.published < timezone.now()

    is_published.boolean = True  # for django admin
    is_published.admin_order_field = 'published'


class SecretPanel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    published = models.DateTimeField('date published', default=timezone.now)
    key_phrase = models.CharField(max_length=500)
    image = models.ImageField(upload_to='secrets')

    archive_text = models.CharField(max_length=200, blank=True, help_text="Overrides 'Archive' button glitching text")
    howto_text = models.CharField(max_length=200, blank=True, help_text="Overrides 'How to Play' button glitching text")
    vote_text = models.CharField(max_length=200, blank=True, help_text="Overrides 'Read + Vote at' label glitching text")
    donate_text = models.CharField(max_length=200, blank=True, help_text="Overrides 'Donate + Vote Further at' label glitching text")

    class Meta:
        ordering = ['published']

    def get_absolute_url(self):
        return reverse('comic-secret-preview', kwargs={'u_id': self.id})
