from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ExpenseStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    MANAGER_APPROVED = "manager_approved", "Manager Approved"
    FINANCE_APPROVED = "finance_approved", "Finance Approved"
    REJECTED = "rejected", "Rejected"


class Expense(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=32,
        choices=ExpenseStatus.choices,
        default=ExpenseStatus.DRAFT,
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_expenses",
    )
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        if self.amount <= Decimal("0.00"):
            raise ValidationError({"amount": "Amount must be greater than zero."})

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"


class ExpenseAttachment(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="expense_attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class AuditEntry(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="audit_entries")
    from_status = models.CharField(max_length=32, choices=ExpenseStatus.choices)
    to_status = models.CharField(max_length=32, choices=ExpenseStatus.choices)
    action = models.CharField(max_length=64)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Audit entries are immutable.")
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.expense_id}: {self.from_status} → {self.to_status}"
