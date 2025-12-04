"""URL configuration for PaymentRequest API v1."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PaymentRequestViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r"payouts", PaymentRequestViewSet, basename="payout")

app_name = "api_v1"

urlpatterns = [
    path("", include(router.urls)),
]
