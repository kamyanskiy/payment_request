"""Admin configuration for request app."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import PaymentRequest


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    """Admin interface for PaymentRequest model."""

    list_display = [
        "id",
        "amount_display",
        "recipient_name",
        "status_badge",
        "created_at",
        "updated_at",
    ]

    list_filter = [
        "status",
        "currency",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "recipient_name",
        "recipient_account",
        "recipient_bank",
        "description",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "processed_at",
    ]

    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": (
                    "amount",
                    "currency",
                    "description",
                ),
            },
        ),
        (
            _("Реквизиты получателя"),
            {
                "fields": (
                    "recipient_name",
                    "recipient_account",
                    "recipient_bank",
                    "recipient_bank_code",
                ),
            },
        ),
        (
            _("Статус и обработка"),
            {
                "fields": (
                    "status",
                    "rejection_reason",
                ),
            },
        ),
        (
            _("Временные метки"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "processed_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    list_per_page = 25
    date_hierarchy = "created_at"

    actions = [
        "approve_requests",
        "reject_requests",
        "complete_requests",
    ]

    def amount_display(self, obj):
        """Display amount with currency."""
        return f"{obj.amount} {obj.currency}"

    amount_display.short_description = _("Сумма")
    amount_display.admin_order_field = "amount"

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            PaymentRequest.Status.PENDING: "#FFA500",
            PaymentRequest.Status.PROCESSING: "#1E90FF",
            PaymentRequest.Status.APPROVED: "#32CD32",
            PaymentRequest.Status.REJECTED: "#DC143C",
            PaymentRequest.Status.COMPLETED: "#228B22",
            PaymentRequest.Status.CANCELLED: "#808080",
        }
        color = colors.get(obj.status, "#000000")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = _("Статус")
    status_badge.admin_order_field = "status"

    @admin.action(description=_("Одобрить выбранные заявки"))
    def approve_requests(self, request, queryset):
        """Approve selected payment requests."""
        updated = 0
        for payment_request in queryset:
            if payment_request.status == PaymentRequest.Status.PENDING:
                payment_request.approve()
                updated += 1

        self.message_user(
            request,
            _(f"Одобрено заявок: {updated}"),
        )

    @admin.action(description=_("Отклонить выбранные заявки"))
    def reject_requests(self, request, queryset):
        """Reject selected payment requests."""
        updated = 0
        for payment_request in queryset:
            if payment_request.status in [
                PaymentRequest.Status.PENDING,
                PaymentRequest.Status.PROCESSING,
            ]:
                payment_request.reject(reason="Отклонено администратором")
                updated += 1

        self.message_user(
            request,
            _(f"Отклонено заявок: {updated}"),
        )

    @admin.action(description=_("Отметить как выполненные"))
    def complete_requests(self, request, queryset):
        """Mark selected payment requests as completed."""
        updated = 0
        for payment_request in queryset:
            if payment_request.status == PaymentRequest.Status.APPROVED:
                payment_request.complete()
                updated += 1

        self.message_user(
            request,
            _(f"Выполнено заявок: {updated}"),
        )
