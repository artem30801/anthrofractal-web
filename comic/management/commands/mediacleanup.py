import os
from collections import defaultdict

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import models


class Command(BaseCommand):
    help = "Prints a list of all files in MEDIA_ROOT that are not referenced in the database."

    def handle(self, *args, **options):
        if not getattr(settings, 'MEDIA_ROOT'):
            raise CommandError("MEDIA_ROOT is not set, nothing to do")

        # Get a list of all files under MEDIA_ROOT
        media = set()
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for f in files:
                media.add(os.path.abspath(os.path.join(root, f)))

        # Get list of all fields (value) for each model (key)
        # that is a FileField or subclass of a FileField
        model_dict = defaultdict(list)
        for model in apps.get_models():
            for field in model._meta.fields:
                if issubclass(field.__class__, models.FileField):
                    model_dict[model].append(field)

        # Get a list of all files referenced in the database
        referenced = set()
        for model in model_dict:
            for db_object in model.objects.all().iterator():
                for field in model_dict[model]:
                    target_file = getattr(db_object, field.name)
                    if target_file:
                        referenced.add(os.path.abspath(target_file.path))

        # Delete and print each file in MEDIA_ROOT that is not referenced in the database
        not_referenced = media - referenced
        print(media)
        print(referenced)
        for filename in not_referenced:
            try:
                os.remove(filename)
                print(f"Removed {filename}")
            except OSError as e:
                print(f"Can not remove {filename}! {e}")
