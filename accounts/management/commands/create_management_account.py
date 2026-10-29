from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
User = get_user_model()

class Command(BaseCommand):
    help = 'Initializes management account'
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True)
        parser.add_argument('--password', type=str, required=True)
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        try:
            user = User.objects.get(username=username)
            if user.role != 'admin': raise CommandError(f"User '{username}' has role '{user.role}'.")
            user.is_superuser = False
            user.is_staff = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Account '{username}' configured."))
        except User.DoesNotExist:
            User.objects.create_user(username=username, password=password, role='admin', is_staff=False, is_superuser=False)
            self.stdout.write(self.style.SUCCESS(f"Created management account '{username}'."))
