"""
Django settings for rok project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from rok.secrets import get_secret


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_secret('DEBUG')

ALLOWED_HOSTS = get_secret('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'account.apps.AccountConfig',
    'apart.apps.ApartConfig',
    'core.apps.CoreConfig',
    'cram.apps.CramConfig',
    'docs.apps.DocsConfig',
    'expen.apps.ExpenConfig',
    'family.apps.FamilyConfig',
    'fuel.apps.FuelConfig',
    'health.apps.HealthConfig',
    'logs.apps.LogsConfig',
    'news.apps.NewsConfig',
    'note.apps.NoteConfig',
    'photo.apps.PhotoConfig',
    'react.apps.ReactConfig',
    'store.apps.StoreConfig',
    'task.apps.TaskConfig',
    'todo.apps.TodoConfig',
    'warr.apps.WarrConfig',
    'weather.apps.WeatherConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django_cprofile_middleware.middleware.ProfilerMiddleware',
]

ROOT_URLCONF = 'rok.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rok.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': get_secret('DATABASE_POSTGRES')
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = get_secret('LANGUAGE_CODE')

TIME_ZONE = get_secret('TIME_ZONE')

USE_I18N = get_secret('USE_I18N')

USE_TZ = get_secret('USE_TZ')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = get_secret('STATICFILES_DIRS')
STATIC_ROOT = BASE_DIR/'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = get_secret('CORS_ORIGIN_WHITELIST')

# DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = get_secret('PROFILING')  # Profiling in Django

USE_THOUSAND_SEPARATOR = True

USE_L10N = True
LOCALE_PATHS = (BASE_DIR/'locale', BASE_DIR/'rok/locale')

MEDIA_ROOT = get_secret('MEDIA_ROOT')
MEDIA_URL = 'media/'

SECURE_SSL_REDIRECT = False  # get_secret('SECURE_SSL_REDIRECT')

#SERVER_EMAIL = get_secret('SERVER_EMAIL')
EMAIL_HOST = get_secret('EMAIL_HOST')
EMAIL_HOST_USER = get_secret('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = get_secret('EMAIL_USE_SSL')
EMAIL_USE_TLS = get_secret('EMAIL_USE_TLS')
EMAIL_ADMIN = get_secret('EMAIL_ADMIN')
EMAIL_DEMOUSER = get_secret('EMAIL_DEMOUSER')
DOMAIN_NAME = get_secret('DOMAIN_NAME')
#CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
DJANGO_PWD_RESET_TOKEN = get_secret('DJANGO_PWD_RESET_TOKEN')
DJANGO_DEMOUSER_PWRD = get_secret('DJANGO_DEMOUSER_PWRD')
DJANGO_HIDE_QTY = get_secret('DJANGO_HIDE_QTY')
DJANGO_HOST = get_secret('DJANGO_HOST')
DJANGO_SERVICE_GROUP = get_secret('DJANGO_SERVICE_GROUP')
DJANGO_SERVICE_PATH = get_secret('DJANGO_SERVICE_PATH')
DJANGO_STORAGE_PATH = get_secret('DJANGO_STORAGE_PATH')
DJANGO_STATIC_ROOT = get_secret('DJANGO_STATIC_ROOT')
DJANGO_MEDIA_ROOT = get_secret('DJANGO_MEDIA_ROOT')
DJANGO_HOST_API = get_secret('DJANGO_HOST_API')
FIREBASE_ACCOUNT_CERT = get_secret('FIREBASE_ACCOUNT_CERT')
DJANGO_DEVICE = get_secret('DJANGO_DEVICE')
DJANGO_HOST_LOG = get_secret('DJANGO_HOST_LOG')
DJANGO_SERVICE_TOKEN = get_secret('DJANGO_SERVICE_TOKEN')
DJANGO_SERVICE_INTERVAL_SEC = get_secret('DJANGO_SERVICE_INTERVAL_SEC')
DJANGO_CERT = get_secret('DJANGO_CERT')
DJANGO_LOG_DEVICE = get_secret('DJANGO_LOG_DEVICE')
DJANGO_LOG_BASE = get_secret('DJANGO_LOG_BASE')
DJANGO_HOST_MAIL = get_secret('DJANGO_HOST_MAIL')
DJANGO_HOST_ADDR = get_secret('DJANGO_HOST_ADDR')
DJANGO_MAIL_ADMIN = get_secret('DJANGO_MAIL_ADMIN')
DJANGO_MAIL_USER = get_secret('DJANGO_MAIL_USER')
DJANGO_MAIL_PWRD = get_secret('DJANGO_MAIL_PWRD')
DJANGO_HOST_FTP = get_secret('DJANGO_HOST_FTP')
DJANGO_FTP_USER = get_secret('DJANGO_FTP_USER')
DJANGO_FTP_PWRD = get_secret('DJANGO_FTP_PWRD')
FAMILY_STORAGE_PATH = get_secret('FAMILY_STORAGE_PATH')
WIN_ACME_WORK = get_secret('WIN_ACME_WORK')
WIN_ACME_CERT = get_secret('WIN_ACME_CERT')
API_WEATHER_KEY = get_secret('API_WEATHER_KEY')
API_WEATHER_TZ = get_secret('API_WEATHER_TZ')
API_WEATHER_CR_URL = get_secret('API_WEATHER_CR_URL')
API_WEATHER_CR_INFO = get_secret('API_WEATHER_CR_INFO')
API_WEATHER_INFO = get_secret('API_WEATHER_INFO')
API_WEATHER_LAT = get_secret('API_WEATHER_LAT')
API_WEATHER_LON = get_secret('API_WEATHER_LON')
API_WHOIS = get_secret('API_WHOIS')
API_COIN_RATE = get_secret('API_COIN_RATE')
API_COIN_RATE_KEY = get_secret('API_COIN_RATE_KEY')
API_COIN_CR_INFO = get_secret('API_COIN_CR_INFO')
API_COIN_CR_URL = get_secret('API_COIN_CR_URL')
API_COIN_INFO = get_secret('API_COIN_INFO')
API_WALLET = get_secret('API_WALLET')
API_WALLET_KEY = get_secret('API_WALLET_KEY')
DJANGO_PYTHON = get_secret('DJANGO_PYTHON')
DJANGO_BACKUP_FOLDER = get_secret('DJANGO_BACKUP_FOLDER')