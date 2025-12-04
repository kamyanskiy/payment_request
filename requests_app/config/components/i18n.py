"""Internationalization settings."""

# https://docs.djangoproject.com/en/5.2/topics/i18n/

import os

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "ru-RU")

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LOCALE_PATH = ["request/locale"]
