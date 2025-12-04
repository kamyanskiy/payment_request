import os
from pathlib import Path

from split_settings.tools import include

# Include all component settings
include(
    "components/common.py",
    "components/database.py",
    "components/installed_apps.py",
    "components/middleware.py",
    "components/template.py",
    "components/auth_validators.py",
    "components/i18n.py",
    "components/rest_framework.py",
)

# Static files
# https://docs.djangoproject.com/en/5.2/howto/static-files/
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Celery settings
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
