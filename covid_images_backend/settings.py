import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.staticfiles',
    'image_list',
]

MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware']

ROOT_URLCONF = 'covid_images_backend.urls'

STATIC_URL = '/static/'
STATICFILES_DIRS = []

# This is a dummy setting for CORS. In production, you should specify allowed origins.
CORS_ALLOW_ALL_ORIGINS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'training/Covid19-dataset')

ALLOWED_HOSTS = ['*']
DEBUG = True

SECRET_KEY = 'dummy'
