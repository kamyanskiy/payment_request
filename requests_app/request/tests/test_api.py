"""Tests for PaymentRequest API."""

from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from request.models import PaymentRequest


class PaymentRequestAPITests(APITestCase):
    """Test cases for PaymentRequest API."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse("api:api_v1:payout-list")
        self.valid_payload = {
            "amount": "1000.00",
            "currency": "RUB",
            "recipient_name": "Test User",
            "recipient_account": "1234567890",
            "description": "Test payment",
        }

    def test_create_payment_request_success(self):
        """Test successful creation of a payment request."""
        # Mock the Celery task to avoid actual execution
        with patch("request.tasks.process_payment_request.apply_async"):
            response = self.client.post(self.url, self.valid_payload)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(PaymentRequest.objects.count(), 1)

            payment_request = PaymentRequest.objects.first()
            self.assertEqual(payment_request.amount, Decimal("1000.00"))
            self.assertEqual(payment_request.status, PaymentRequest.Status.PENDING)
            self.assertEqual(payment_request.recipient_name, "Test User")

    def test_create_payment_request_triggers_celery(self):
        """Test that Celery task is triggered upon creation."""
        with patch("request.tasks.process_payment_request.apply_async") as mock_task:
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(self.url, self.valid_payload)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Verify task was called with the correct ID and countdown
            payment_request = PaymentRequest.objects.first()
            mock_task.assert_called_once_with(
                args=[payment_request.id],
                countdown=2,
            )

    def test_create_payment_request_invalid_amount(self):
        """Test validation for negative/zero amount."""
        payload = self.valid_payload.copy()
        payload["amount"] = "-100.00"

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data)
        self.assertEqual(PaymentRequest.objects.count(), 0)

    def test_create_payment_request_invalid_account(self):
        """Test validation for non-digit account."""
        payload = self.valid_payload.copy()
        payload["recipient_account"] = "invalid123"

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recipient_account", response.data)
        self.assertEqual(PaymentRequest.objects.count(), 0)

    def test_get_payment_request_list(self):
        """Test retrieving list of payment requests."""
        # Create some requests
        PaymentRequest.objects.create(
            amount=Decimal("100.00"),
            recipient_name="User 1",
            recipient_account="111",
        )
        PaymentRequest.objects.create(
            amount=Decimal("200.00"),
            recipient_name="User 2",
            recipient_account="222",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
