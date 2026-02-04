from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from expenses.api.serializers import AuditEntrySerializer, ExpenseSerializer
from expenses.models import AuditEntry, Expense
from expenses.services import TransitionRequest, transition_expense


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().select_related("submitted_by")
    serializer_class = ExpenseSerializer

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        expense = self.get_object()
        target_status = request.data.get("target_status")
        reason = request.data.get("reason", "")
        transition_request = TransitionRequest(
            expense=expense,
            target_status=target_status,
            actor=request.user,
            reason=reason,
        )
        expense = transition_expense(transition_request)
        serializer = self.get_serializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="audit")
    def audit_entries(self, request, pk=None):
        expense = self.get_object()
        entries = AuditEntry.objects.filter(expense=expense).select_related("actor")
        serializer = AuditEntrySerializer(entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuditEntryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AuditEntry.objects.all().select_related("expense", "actor")
    serializer_class = AuditEntrySerializer
