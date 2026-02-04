from dataclasses import dataclass
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from expenses.models import AuditEntry, Expense, ExpenseStatus

FINANCE_APPROVAL_THRESHOLD = Decimal("1000.00")


@dataclass(frozen=True)
class TransitionRequest:
    expense: Expense
    target_status: str
    actor
    reason: str = ""


def _user_in_group(user, group_name: str) -> bool:
    return Group.objects.filter(name=group_name, user=user).exists()


def _ensure_actor_permission(expense: Expense, target_status: str, actor) -> None:
    if target_status == ExpenseStatus.SUBMITTED and actor != expense.submitted_by:
        raise PermissionDenied("Only the submitter can submit an expense.")
    if target_status == ExpenseStatus.MANAGER_APPROVED and not _user_in_group(actor, "manager"):
        raise PermissionDenied("Only managers can approve at this step.")
    if target_status == ExpenseStatus.FINANCE_APPROVED and not _user_in_group(actor, "finance"):
        raise PermissionDenied("Only finance can approve at this step.")
    if target_status == ExpenseStatus.REJECTED and not (
        _user_in_group(actor, "manager") or _user_in_group(actor, "finance")
    ):
        raise PermissionDenied("Only managers or finance can reject expenses.")


def _validate_transition(expense: Expense, target_status: str, reason: str) -> None:
    valid_transitions = {
        ExpenseStatus.DRAFT: {ExpenseStatus.SUBMITTED},
        ExpenseStatus.SUBMITTED: {ExpenseStatus.MANAGER_APPROVED, ExpenseStatus.REJECTED},
        ExpenseStatus.MANAGER_APPROVED: {ExpenseStatus.FINANCE_APPROVED, ExpenseStatus.REJECTED},
        ExpenseStatus.REJECTED: {ExpenseStatus.SUBMITTED},
    }

    allowed_targets = valid_transitions.get(expense.status, set())
    if target_status not in allowed_targets:
        raise ValidationError("Invalid status transition.")

    if target_status == ExpenseStatus.FINANCE_APPROVED and expense.amount < FINANCE_APPROVAL_THRESHOLD:
        raise ValidationError("Finance approval is only required for high-value expenses.")

    if target_status == ExpenseStatus.REJECTED and not reason.strip():
        raise ValidationError("A rejection reason is required.")


@transaction.atomic
def transition_expense(request: TransitionRequest) -> Expense:
    expense = request.expense
    target_status = request.target_status
    actor = request.actor

    _validate_transition(expense, target_status, request.reason)
    _ensure_actor_permission(expense, target_status, actor)

    previous_status = expense.status
    expense.status = target_status
    if target_status == ExpenseStatus.REJECTED:
        expense.rejection_reason = request.reason
    elif target_status == ExpenseStatus.SUBMITTED:
        expense.rejection_reason = ""

    expense.save(update_fields=["status", "rejection_reason", "updated_at"])

    AuditEntry.objects.create(
        expense=expense,
        from_status=previous_status,
        to_status=target_status,
        action="transition",
        actor=actor,
        reason=request.reason,
    )

    return expense
