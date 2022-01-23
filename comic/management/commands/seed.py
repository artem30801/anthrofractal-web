from django.core.management.base import BaseCommand

import sys
import random

from faker import Faker
from tqdm import tqdm

from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

from comic.models import PanelTag, Page, ComicPanel, SecretPanel


class Command(BaseCommand):
    help = "seed database for testing and development"

    fake: Faker

    def add_arguments(self, parser):
        parser.add_argument('number', type=int, help="number of panels to generate")
        # parser.add_argument('seed', type=int, help="random seed")

    def handle(self, *args, **options):
        number = options.get('number', 10)
        seed = options.get('seed', 0)

        self.fake = Faker()
        self.fake.seed_instance(seed)
        random.seed(seed)

        self.stdout.write('Seeding data...')
        self.seed_tags(round(number*1.1))
        self.seed_pages(min(number, max(round(number/10), 5)))
        self.seed_panels(number, seed=seed)
        self.seed_secrets(min(number, max(round(number/5), 5)), seed=seed)
        self.stdout.write('Seeding complete.')

    def seed_tags(self, count: int):
        self.stdout.write('Deleting old tags...')
        PanelTag.objects.all().delete()

        for _ in tqdm(range(count), desc="Seeding tags", file=sys.stdout):
            slug: str = self.fake.unique.slug()
            name = slug.replace('-', " ")
            tag = PanelTag(name=name, slug=slug)
            tag.save()

    def seed_pages(self, count: int):
        self.stdout.write('Deleting old pages...')
        Page.objects.all().delete()

        for _ in tqdm(range(count), desc="Seeding pages", file=sys.stdout):
            title: str = self.fake.sentence()
            page = Page(number=0, title=title)
            page.save()

    def seed_panels(self, count: int, seed=0):
        self.stdout.write('Deleting old comic panels...')
        for panel in SecretPanel.objects.all():
            panel.image.delete(save=True)
            panel.delete()

        tags = list(PanelTag.objects.all())
        pages = list(Page.objects.all())
        num_pages = len(pages)

        for i in tqdm(range(count), desc="Seeding panels", file=sys.stdout):
            title: str = self.fake.sentence()
            alt: str = self.fake.sentence()
            page = pages[int(i / count * num_pages)]

            tag_count = random.randint(0, 5)
            panel_tags = self.fake.random_elements(elements=tags, unique=True, length=tag_count)

            panel = ComicPanel(number=0,
                               title=title,
                               alt=alt,
                               page=page,
                               tags=panel_tags,
                               )
            panel.save()

            image = save_img("https://picsum.photos/1080")
            panel.image.save(f"panel-{panel.pk}.png", image)
            panel.save()

    def seed_secrets(self, count: int, seed=0):
        self.stdout.write('Deleting old secret panels...')
        for panel in SecretPanel.objects.all():
            panel.image.delete(save=True)
            panel.delete()

        for _ in tqdm(range(count), desc="Seeding secrets", file=sys.stdout):
            key_phrase: str = self.fake.unique.slug().replace('-', ' ')
            archive_text: str = self.fake.sentence(nb_words=1)
            howto_text: str = self.fake.sentence(nb_words=2)
            vote_text: str = self.fake.sentence(nb_words=3)
            donate_text: str = self.fake.sentence(nb_words=4)

            panel = SecretPanel(key_phrase=key_phrase,
                                archive_text=archive_text,
                                howto_text=howto_text,
                                vote_text=vote_text,
                                donate_text=donate_text
                                )

            panel.save()

            image = save_img("https://picsum.photos/1080")
            panel.image.save(f"secret-{self.fake.slug(key_phrase)}.png", image)
            panel.save()


def save_img(url):
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urlopen(url).read())
    img_temp.flush()
    return File(img_temp)
