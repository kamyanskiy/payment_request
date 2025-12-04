"""Signals for request app."""

import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PaymentRequest

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PaymentRequest)
def trigger_payment_processing(sender, instance, created, **kwargs):
    """
    Trigger async processing when a new PaymentRequest is created.

    Only triggers if:
    - It's a new record (created=True)
    - Status is PENDING
    """
    if created and instance.status == PaymentRequest.Status.PENDING:
        # Import here to avoid circular imports
        from .tasks import process_payment_request

        # Use on_commit to ensure task runs after transaction commits
        # Add countdown as extra safety for race conditions
        transaction.on_commit(
            lambda: process_payment_request.apply_async(
                args=[instance.id],
                countdown=2,  # Wait 2 seconds before execution
            )
        )
        logger.info(f"Scheduled processing task for PaymentRequest #{instance.id} (2s delay)")
