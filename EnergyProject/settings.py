"""
Django settings for EnergyProject project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1+*ucs@g9#_w3hjtwlag#agf2tdkz%7b-5ini(j62p%&f^a8y0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','re-energise.herokuapp.com','.vercel.app', 'energy-system-production.up.railway.app','re-energise.xyz']
CSRF_TRUSTED_ORIGINS = ['https://energy-system-production.up.railway.app','https://re-energise.xyz']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'livereload',
    'django.contrib.staticfiles',

    # own
    'EnergyApp.apps.EnergyappConfig',
    'crispy_forms',
    'crispy_bootstrap5',
    'bootstrap5',
]

CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'EnergyApp.middleware.LoginMiddleware',
    'livereload.middleware.LiveReloadScript',
]

ROOT_URLCONF = 'EnergyProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'EnergyProject.wsgi.application'



# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Commented out due to being sensitive info',
        'USER': 'Commented out due to being sensitive info',
        'PASSWORD': 'Commented out due to being sensitive info',
        'HOST': 'Commented out due to being sensitive info',
        'PORT': 'Commented out due to being sensitive info',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
from google.oauth2 import service_account
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, 'credential.json')
)
DEFAULT_FILE_STORAGE='EnergyProject.gcloud.GoogleCloudMediaFileStorage'
GS_PROJECT_ID = 're-energise-380012'
GS_BUCKET_NAME = 're-energise'
MEDIA_ROOT = "media/"
UPLOAD_ROOT = 'media/uploads/'
MEDIA_URL = 'https://storage.googleapis.com/{}/'.format(GS_BUCKET_NAME)

STATIC_URL = 'static/'
# MEDIA_URL = '/profiles/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES = [
    os.path.join(BASE_DIR, 'static')
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
# MEDIA_ROOT = os.path.join(BASE_DIR, 'profiles')

LOGIN_REDIRECT_URL = '/dashboard'
LOGOUT_REDIRECT_URL = '/'

# SMTP Config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'Commented out due to being sensitive info'
EMAIL_PORT = 'Commented out due to being sensitive info'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'Commented out due to being sensitive info'
EMAIL_HOST_PASSWORD = 'Commented out due to being sensitive info'