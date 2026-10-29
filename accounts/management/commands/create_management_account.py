import getpass
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Initializes the dedicated application management account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Management username')
        parser.add_argument('--email', type=str, default='admin@system.local', help='Management email')
        parser.add_argument('--password', type=str, required=False, help='Management password (optional, will prompt if omitted)')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password')

        try:
            user = User.objects.get(username=username)
            if user.role != 'admin':
                raise CommandError(
                    f"User '{username}' exists but has role '{user.role}'. "
                    f"Cannot convert to management account."
                )
            if user.is_superuser or user.is_staff:
                self.stdout.write(self.style.WARNING(
                    f"User '{username}' has superuser/staff flags. "
                    f"Clearing them to enforce custom role architecture."
                ))
                user.is_superuser = False
                user.is_staff = False
                user.save()
            self.stdout.write(self.style.SUCCESS(
                f"Management account '{username}' already exists and is correctly configured."
            ))
        except User.DoesNotExist:
            self.stdout.write(f"Creating management account '{username}'...")
            
            if not password:
                password = getpass.getpass("Enter password for management account: ")
            
            if not password:
                raise CommandError("Password cannot be empty.")

            if not options.get('password'):
                password2 = getpass.getpass("Confirm password: ")
                if password != password2:
                    raise CommandError("Passwords do not match.")

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='admin',
                is_staff=False,
                is_superuser=False
            )
            self.stdout.write(self.style.SUCCESS(
                f"Successfully created management account '{username}'."
            ))
