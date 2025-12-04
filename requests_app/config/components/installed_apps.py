"""Installed Django applications."""

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "drf_spectacular",
    "debug_toolbar",
    "django_celery_beat",
    # Local apps
    "request.apps.RequestConfig",
]
