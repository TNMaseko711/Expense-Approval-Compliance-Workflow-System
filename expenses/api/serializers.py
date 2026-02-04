from rest_framework import serializers

from expenses.models import AuditEntry, Expense, ExpenseAttachment, ExpenseStatus


class ExpenseAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseAttachment
        fields = ["id", "file", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class ExpenseSerializer(serializers.ModelSerializer):
    attachments = ExpenseAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "description",
            "amount",
            "status",
            "submitted_by",
            "rejection_reason",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "rejection_reason",
            "submitted_by",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["submitted_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.status in {ExpenseStatus.MANAGER_APPROVED, ExpenseStatus.FINANCE_APPROVED}:
            raise serializers.ValidationError("Approved expenses cannot be modified.")
        if instance.status == ExpenseStatus.REJECTED:
            raise serializers.ValidationError("Rejected expenses must be resubmitted.")
        return super().update(instance, validated_data)


class AuditEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEntry
        fields = [
            "id",
            "from_status",
            "to_status",
            "action",
            "actor",
            "reason",
            "created_at",
        ]
        read_only_fields = fields
