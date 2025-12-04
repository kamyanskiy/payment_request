"""URL configuration for PaymentRequest API."""

from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("v1/", include("request.api.v1.urls")),
]
