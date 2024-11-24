# settings.py

from pathlib import Path
import os
from django.contrib.messages import constants as messages
from decouple import config
from storages.backends.s3boto3 import S3Boto3Storage

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # If needed for CORS

    # Your custom apps
    'home',
    'user',
    'client_app',
    'customer_app',
    'customer_journey_app',
    'dashboard_app',
    'funding_route_app',
    'hr_app',
    'product_app',
    'admin_app',
    'region_app',
    'security_app',
    'question_actions_requirements_app',

    # Libraries for two-factor authentication
    'django_otp',
    'django_otp.plugins.otp_email',  # OTP via Email
    'two_factor',
    'tempus_dominus',
    'bootstrap_datepicker_plus',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # Required for OTP
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'reform_crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'client_app', 'templates'),
            os.path.join(BASE_DIR, 'customer_app', 'templates'),
            os.path.join(BASE_DIR, 'customer_journey_app', 'templates'),
            os.path.join(BASE_DIR, 'dashboard_app', 'templates'),
            os.path.join(BASE_DIR, 'funding_route_app', 'templates'),
            os.path.join(BASE_DIR, 'hr_app', 'templates'),
            os.path.join(BASE_DIR, 'product_app', 'templates'),
            os.path.join(BASE_DIR, 'region_app', 'templates'),
            os.path.join(BASE_DIR, 'question_actions_requirements_app', 'templates'),
            os.path.join(BASE_DIR, 'admin_app', 'templates'),
            os.path.join(BASE_DIR, 'security_app', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


WSGI_APPLICATION = 'reform_crm.wsgi.application'

# Database configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Using SQLite for simplicity
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'reform',
#         'USER': 'reform',
#         'PASSWORD': 'Reform@123',
#         'HOST': '35.179.137.230',
#         'PORT': 5432,
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'reformCRM',
#         'USER': 'postgres',
#         'PASSWORD': 'Gowtham839938',
#         'HOST': 'localhost',
#         'PORT': 5432,
#     }
# }

MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# Authentication settings
AUTH_USER_MODEL = 'user.User'

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Here I am using gmail smtp server
EMAIL_PORT = 587  # gmail smtp server port
EMAIL_HOST_USER = "support@reform-group.uk"  # Use your email account
EMAIL_HOST_PASSWORD = "nrhethtofrfhryjo"  # For gmail use app password
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Security settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True

# Django's default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Enable trusted origins for CSRF (adjust if needed)
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://reformcrm.up.railway.app/',
    'https://reformcrm-beta-0c709f5.kuberns.com',
    'https://myreform.uk',
]

# Ensure Two Factor Authentication URLs
LOGIN_URL = '/user/login'

MEDIAFILES_LOCATION = 'media'

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')

class MediaStorage(S3Boto3Storage):
    location = MEDIAFILES_LOCATION
    file_overwrite = False

DEFAULT_FILE_STORAGE = 'reform_crm.settings.MediaStorage'
AWS_DEFAULT_ACL = 'private'
AWS_S3_ADDRESSING_STYLE = 'virtual'

MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{MEDIAFILES_LOCATION}/'