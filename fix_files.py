import os

settings_content = """import os
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-replace-in-prod')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'accounts', 'academics', 'attendance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {'default': dj_database_url.parse(os.environ.get('DATABASE_URL', 'sqlite:///' + str(BASE_DIR / 'db.sqlite3')), conn_max_age=600, ssl_require=os.environ.get('DATABASE_URL') is not None)}

AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(str(BASE_DIR), 'staticfiles')
STORAGES = {"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}, "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(str(BASE_DIR), 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

MESSAGE_TAGS = {messages.DEBUG: 'alert-secondary', messages.INFO: 'alert-info', messages.SUCCESS: 'alert-success', messages.WARNING: 'alert-warning', messages.ERROR: 'alert-danger'}
"""

models_content = """from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (('admin', 'Administrator'), ('lecturer', 'Lecturer'), ('student', 'Student'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    groups = models.ManyToManyField('auth.Group', related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_permissions', blank=True)
    def __str__(self): return self.username

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)

class LecturerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='lecturer_profile')
    staff_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
"""

cmd_content = """from django.core.management.base import BaseCommand, CommandError
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
"""

os.makedirs('accounts/management/commands', exist_ok=True)
open('accounts/management/commands/__init__.py', 'w').close()

with open('core/settings.py', 'w', encoding='utf-8') as f: f.write(settings_content)
with open('accounts/models.py', 'w', encoding='utf-8') as f: f.write(models_content)
with open('accounts/management/commands/create_management_account.py', 'w', encoding='utf-8') as f: f.write(cmd_content)

print('FILES OVERWRITTEN SUCCESSFULLY!')
