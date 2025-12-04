"""Serializers for PaymentRequest API v1."""

from decimal import Decimal

from rest_framework import serializers

from request.models import PaymentRequest


class PaymentRequestSerializer(serializers.ModelSerializer):
    """Serializer for PaymentRequest model."""

    # Read-only computed fields
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    currency_display = serializers.CharField(
        source="get_currency_display",
        read_only=True,
    )

    class Meta:
        model = PaymentRequest
        fields = [
            "id",
            "amount",
            "currency",
            "currency_display",
            "recipient_name",
            "recipient_account",
            "recipient_bank",
            "recipient_bank_code",
            "status",
            "status_display",
            "description",
            "created_at",
            "updated_at",
            "processed_at",
            "rejection_reason",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "processed_at",
        ]

    def validate_amount(self, value):
        """Validate that amount is positive."""
        if value <= Decimal("0"):
            raise serializers.ValidationError("Сумма выплаты должна быть больше нуля.")
        return value

    def validate_recipient_account(self, value):
        """Validate recipient account number."""
        if not value or not value.strip():
            raise serializers.ValidationError("Номер счета получателя не может быть пустым.")

        # Check if account contains only digits
        if not value.isdigit():
            raise serializers.ValidationError("Номер счета должен содержать только цифры.")

        return value.strip()

    def validate(self, attrs):
        """Cross-field validation."""
        # If status is being changed to rejected, rejection_reason should be provided
        if attrs.get("status") == PaymentRequest.Status.REJECTED:
            if not attrs.get("rejection_reason"):
                raise serializers.ValidationError({"rejection_reason": "Необходимо указать причину отклонения."})

        return attrs


class PaymentRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PaymentRequest."""

    class Meta:
        model = PaymentRequest
        fields = [
            "amount",
            "currency",
            "recipient_name",
            "recipient_account",
            "recipient_bank",
            "recipient_bank_code",
            "description",
        ]

    def validate_amount(self, value):
        """Validate that amount is positive."""
        if value <= Decimal("0"):
            raise serializers.ValidationError("Сумма выплаты должна быть больше нуля.")
        return value

    def validate_recipient_account(self, value):
        """Validate recipient account number."""
        if not value or not value.strip():
            raise serializers.ValidationError("Номер счета получателя не может быть пустым.")

        # Check if account contains only digits
        if not value.isdigit():
            raise serializers.ValidationError("Номер счета должен содержать только цифры.")

        return value.strip()

    def create(self, validated_data):
        """Create new payment request with pending status."""
        validated_data["status"] = PaymentRequest.Status.PENDING
        return super().create(validated_data)


class PaymentRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating PaymentRequest (primarily status)."""

    class Meta:
        model = PaymentRequest
        fields = [
            "status",
            "rejection_reason",
            "description",
        ]

    def validate_status(self, value):
        """Validate status transitions."""
        instance = self.instance
        if not instance:
            return value

        current_status = instance.status

        # Define allowed status transitions
        allowed_transitions = {
            PaymentRequest.Status.PENDING: [
                PaymentRequest.Status.PROCESSING,
                PaymentRequest.Status.APPROVED,
                PaymentRequest.Status.REJECTED,
                PaymentRequest.Status.CANCELLED,
            ],
            PaymentRequest.Status.PROCESSING: [
                PaymentRequest.Status.APPROVED,
                PaymentRequest.Status.REJECTED,
                PaymentRequest.Status.CANCELLED,
            ],
            PaymentRequest.Status.APPROVED: [
                PaymentRequest.Status.COMPLETED,
                PaymentRequest.Status.CANCELLED,
            ],
        }

        # Check if transition is allowed
        if current_status in allowed_transitions:
            if value not in allowed_transitions[current_status]:
                raise serializers.ValidationError(
                    f"Невозможно изменить статус с '{instance.get_status_display()}' "
                    f"на '{PaymentRequest.Status(value).label}'."
                )
        elif current_status in [
            PaymentRequest.Status.COMPLETED,
            PaymentRequest.Status.REJECTED,
            PaymentRequest.Status.CANCELLED,
        ]:
            raise serializers.ValidationError("Невозможно изменить статус завершенной/отклоненной/отмененной заявки.")

        return value

    def validate(self, attrs):
        """Cross-field validation."""
        # If status is being changed to rejected, rejection_reason should be provided
        if attrs.get("status") == PaymentRequest.Status.REJECTED:
            if not attrs.get("rejection_reason") and not self.instance.rejection_reason:
                raise serializers.ValidationError({"rejection_reason": "Необходимо указать причину отклонения."})

        return attrs

    def update(self, instance, validated_data):
        """Update payment request and handle status-specific logic."""
        new_status = validated_data.get("status")

        # If status is being changed to completed, set processed_at
        if new_status == PaymentRequest.Status.COMPLETED and instance.status != new_status:
            from django.utils import timezone

            validated_data["processed_at"] = timezone.now()

        return super().update(instance, validated_data)


class PaymentRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = PaymentRequest
        fields = [
            "id",
            "amount",
            "currency",
            "recipient_name",
            "status",
            "status_display",
            "created_at",
        ]
