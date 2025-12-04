"""Celery tasks for request app."""

import logging
import random
import time

from celery import shared_task
from django.db import transaction

from .models import PaymentRequest

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_payment_request(self, request_id):
    """
    Process a payment request asynchronously.

    Simulates external system interaction:
    1. Validates the request state
    2. Simulates processing delay
    3. Updates status based on simulated outcome
    """
    logger.info(f"Starting processing for PaymentRequest #{request_id}")

    try:
        # Get the request with a lock to prevent race conditions
        with transaction.atomic():
            payment_request = PaymentRequest.objects.select_for_update().get(id=request_id)

            # Check if status is still PENDING
            if payment_request.status != PaymentRequest.Status.PENDING:
                logger.warning(
                    f"PaymentRequest #{request_id} is not PENDING (status: {payment_request.status}). Skipping."
                )
                return f"Skipped: Status is {payment_request.status}"

            # Update status to PROCESSING
            payment_request.status = PaymentRequest.Status.PROCESSING
            payment_request.save(update_fields=["status", "updated_at"])
            logger.info(f"PaymentRequest #{request_id} status changed to PROCESSING")

    except PaymentRequest.DoesNotExist:
        logger.error(f"PaymentRequest #{request_id} not found")
        return "Failed: Request not found"

    # Simulate external processing (outside the lock)
    # In a real scenario, this would be an API call to a payment gateway
    processing_time = random.uniform(2.0, 5.0)
    time.sleep(processing_time)

    # Simulate random success/failure
    # 90% success rate
    is_success = random.random() < 0.9

    with transaction.atomic():
        # Re-fetch to get fresh data
        payment_request = PaymentRequest.objects.select_for_update().get(id=request_id)

        if is_success:
            payment_request.approve()
            logger.info(f"PaymentRequest #{request_id} successfully APPROVED")
            result = "Approved"
        else:
            reason = "Rejected by external system (simulated failure)"
            payment_request.reject(reason=reason)
            logger.warning(f"PaymentRequest #{request_id} REJECTED: {reason}")
            result = "Rejected"

    return f"Processed in {processing_time:.2f}s: {result}"
