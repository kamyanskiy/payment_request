"""Common Django settings."""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-qct7jn4#wri&ox&wg&*0%jtmow4*!*i-r!8g$i0ovh+n4a$5-t")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Application definition
ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
