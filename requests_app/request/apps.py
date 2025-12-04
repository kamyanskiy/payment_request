from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RequestConfig(AppConfig):
    """Configuration for the request application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "request"
    verbose_name = _("Request")

    def ready(self):
        """Import signals when app is ready."""
        import request.signals  # noqa: F401
