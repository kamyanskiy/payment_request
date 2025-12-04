"""Payment request models."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentRequest(models.Model):
    """
    Модель заявки на выплату средств.

    Представляет заявку на перевод денежных средств получателю
    с отслеживанием статуса и истории изменений.
    """

    class Status(models.TextChoices):
        """Статусы заявки на выплату."""

        PENDING = "pending", _("Ожидает обработки")
        PROCESSING = "processing", _("В обработке")
        APPROVED = "approved", _("Одобрена")
        REJECTED = "rejected", _("Отклонена")
        COMPLETED = "completed", _("Выполнена")
        CANCELLED = "cancelled", _("Отменена")

    class Currency(models.TextChoices):
        """Поддерживаемые валюты."""

        RUB = "RUB", _("Российский рубль")
        USD = "USD", _("Доллар США")
        EUR = "EUR", _("Евро")
        GBP = "GBP", _("Фунт стерлингов")

    # Основные поля
    amount = models.DecimalField(
        _("Сумма выплаты"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("Сумма выплаты (должна быть больше 0)"),
    )

    currency = models.CharField(
        _("Валюта"),
        max_length=3,
        choices=Currency.choices,
        default=Currency.RUB,
    )

    # Реквизиты получателя
    recipient_name = models.CharField(
        _("Имя получателя"),
        max_length=255,
        help_text=_("Полное имя или название организации получателя"),
    )

    recipient_account = models.CharField(
        _("Номер счета получателя"),
        max_length=100,
        help_text=_("Банковский счет, номер карты или другой идентификатор"),
    )

    recipient_bank = models.CharField(
        _("Банк получателя"),
        max_length=255,
        blank=True,
        help_text=_("Название банка получателя (опционально)"),
    )

    recipient_bank_code = models.CharField(
        _("БИК/SWIFT банка"),
        max_length=50,
        blank=True,
        help_text=_("БИК, SWIFT или другой код банка (опционально)"),
    )

    # Статус и метаданные
    status = models.CharField(
        _("Статус заявки"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    description = models.TextField(
        _("Описание/Комментарий"),
        blank=True,
        help_text=_("Дополнительная информация о выплате"),
    )

    # Временные метки
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
    )

    # Дополнительные поля для аудита
    processed_at = models.DateTimeField(
        _("Дата обработки"),
        null=True,
        blank=True,
        help_text=_("Дата и время обработки заявки"),
    )

    rejection_reason = models.TextField(
        _("Причина отклонения"),
        blank=True,
        help_text=_("Причина отклонения заявки (если применимо)"),
    )

    class Meta:
        """Метаданные модели."""

        verbose_name = _("Заявка на выплату")
        verbose_name_plural = _("Заявки на выплату")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at", "status"]),
            models.Index(fields=["recipient_account"]),
        ]

    def __str__(self):
        """Строковое представление заявки."""
        return f"Заявка #{self.pk} - {self.amount} {self.currency} ({self.get_status_display()})"

    def __repr__(self):
        """Техническое представление заявки."""
        return f"<PaymentRequest(id={self.pk}, amount={self.amount}, currency={self.currency}, status={self.status})>"

    @property
    def is_pending(self):
        """Проверка, находится ли заявка в ожидании."""
        return self.status == self.Status.PENDING

    @property
    def is_completed(self):
        """Проверка, завершена ли заявка."""
        return self.status == self.Status.COMPLETED

    @property
    def can_be_cancelled(self):
        """Проверка, может ли заявка быть отменена."""
        return self.status in [self.Status.PENDING, self.Status.PROCESSING]

    def approve(self):
        """Одобрить заявку."""
        if self.status == self.Status.PENDING:
            self.status = self.Status.APPROVED
            self.save(update_fields=["status", "updated_at"])

    def reject(self, reason=""):
        """Отклонить заявку."""
        if self.status in [self.Status.PENDING, self.Status.PROCESSING]:
            self.status = self.Status.REJECTED
            self.rejection_reason = reason
            self.save(update_fields=["status", "rejection_reason", "updated_at"])

    def complete(self):
        """Отметить заявку как выполненную."""
        if self.status == self.Status.APPROVED:
            self.status = self.Status.COMPLETED
            from django.utils import timezone

            self.processed_at = timezone.now()
            self.save(update_fields=["status", "processed_at", "updated_at"])

    def cancel(self):
        """Отменить заявку."""
        if self.can_be_cancelled:
            self.status = self.Status.CANCELLED
            self.save(update_fields=["status", "updated_at"])
