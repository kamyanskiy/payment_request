"""Views for PaymentRequest API v1."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from request.models import PaymentRequest

from .serializers import (
    PaymentRequestCreateSerializer,
    PaymentRequestListSerializer,
    PaymentRequestSerializer,
    PaymentRequestUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Список заявок на выплату",
        description="Получить список всех заявок на выплату с пагинацией и фильтрацией.",
        tags=["Заявки на выплату"],
    ),
    retrieve=extend_schema(
        summary="Получить заявку по ID",
        description="Получить детальную информацию о заявке на выплату по идентификатору.",
        tags=["Заявки на выплату"],
    ),
    create=extend_schema(
        summary="Создать новую заявку",
        description="Создать новую заявку на выплату. Статус автоматически устанавливается в 'pending', после чего запускается асинхронная обработка.",
        tags=["Заявки на выплату"],
    ),
    partial_update=extend_schema(
        summary="Частично обновить заявку",
        description="Частично обновить заявку на выплату (в основном для изменения статуса).",
        tags=["Заявки на выплату"],
    ),
    destroy=extend_schema(
        summary="Удалить заявку",
        description="Удалить заявку на выплату по идентификатору.",
        tags=["Заявки на выплату"],
    ),
)
class PaymentRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заявками на выплату.

    Предоставляет CRUD операции для модели PaymentRequest:
    - GET /api/v1/payouts/ - список заявок
    - GET /api/v1/payouts/{id}/ - получение заявки
    - POST /api/v1/payouts/ - создание заявки
    - PATCH /api/v1/payouts/{id}/ - частичное обновление
    - DELETE /api/v1/payouts/{id}/ - удаление заявки
    """

    queryset = PaymentRequest.objects.all()
    serializer_class = PaymentRequestSerializer

    # Filtering and search
    search_fields = [
        "recipient_name",
        "recipient_account",
        "description",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "amount",
        "status",
    ]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == "list":
            return PaymentRequestListSerializer
        elif self.action == "create":
            return PaymentRequestCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PaymentRequestUpdateSerializer
        return PaymentRequestSerializer

    def get_queryset(self):
        """
        Optionally filter queryset by status and currency.

        Query parameters:
        - status: filter by status (e.g., ?status=pending)
        - currency: filter by currency (e.g., ?currency=RUB)
        - min_amount: filter by minimum amount (e.g., ?min_amount=1000)
        - max_amount: filter by maximum amount (e.g., ?max_amount=10000)
        """
        queryset = super().get_queryset()

        # Filter by status
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by currency
        currency_param = self.request.query_params.get("currency")
        if currency_param:
            queryset = queryset.filter(currency=currency_param)

        # Filter by amount range
        min_amount = self.request.query_params.get("min_amount")
        if min_amount:
            try:
                queryset = queryset.filter(amount__gte=min_amount)
            except (ValueError, TypeError):
                pass

        max_amount = self.request.query_params.get("max_amount")
        if max_amount:
            try:
                queryset = queryset.filter(amount__lte=max_amount)
            except (ValueError, TypeError):
                pass

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new payment request."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Return full serializer for response
        response_serializer = PaymentRequestSerializer(serializer.instance)
        headers = self.get_success_headers(response_serializer.data)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        """
        Save instance.

        The post_save signal will automatically trigger async processing.
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """Full update is not allowed, use partial_update instead."""
        return Response(
            {"detail": "Используйте PATCH для частичного обновления заявки."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        """Partially update a payment request."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return full serializer for response
        response_serializer = PaymentRequestSerializer(serializer.instance)

        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a payment request."""
        instance = self.get_object()

        # Check if payment can be deleted
        if instance.status in [
            PaymentRequest.Status.COMPLETED,
            PaymentRequest.Status.PROCESSING,
        ]:
            return Response(
                {"detail": f"Невозможно удалить заявку в статусе '{instance.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Одобрить заявку",
        description="Одобрить заявку на выплату (изменить статус на 'approved').",
        tags=["Заявки на выплату"],
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a payment request."""
        instance = self.get_object()

        if instance.status != PaymentRequest.Status.PENDING:
            return Response(
                {"detail": f"Невозможно одобрить заявку в статусе '{instance.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.approve()
        serializer = PaymentRequestSerializer(instance)

        return Response(serializer.data)

    @extend_schema(
        summary="Отклонить заявку",
        description="Отклонить заявку на выплату с указанием причины.",
        tags=["Заявки на выплату"],
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a payment request."""
        instance = self.get_object()
        reason = request.data.get("reason", "")

        if instance.status not in [
            PaymentRequest.Status.PENDING,
            PaymentRequest.Status.PROCESSING,
        ]:
            return Response(
                {"detail": f"Невозможно отклонить заявку в статусе '{instance.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.reject(reason=reason)
        serializer = PaymentRequestSerializer(instance)

        return Response(serializer.data)

    @extend_schema(
        summary="Завершить заявку",
        description="Отметить заявку как выполненную (изменить статус на 'completed').",
        tags=["Заявки на выплату"],
    )
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Complete a payment request."""
        instance = self.get_object()

        if instance.status != PaymentRequest.Status.APPROVED:
            return Response(
                {"detail": f"Невозможно завершить заявку в статусе '{instance.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.complete()
        serializer = PaymentRequestSerializer(instance)

        return Response(serializer.data)

    @extend_schema(
        summary="Отменить заявку",
        description="Отменить заявку на выплату.",
        tags=["Заявки на выплату"],
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a payment request."""
        instance = self.get_object()

        if not instance.can_be_cancelled:
            return Response(
                {"detail": f"Невозможно отменить заявку в статусе '{instance.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.cancel()
        serializer = PaymentRequestSerializer(instance)

        return Response(serializer.data)
