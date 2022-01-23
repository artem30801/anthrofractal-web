from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        User = get_user_model()

        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError(f"There is no user named {options['username']}")

        self.stdout.write(f"Making {options.get('username')} superuser")
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.set_unusable_password()
        user.save()
        self.stdout.write("Done")
