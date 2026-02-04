from django.urls import include, path
from rest_framework.routers import DefaultRouter

from expenses.api.views import AuditEntryViewSet, ExpenseViewSet

router = DefaultRouter()
router.register("expenses", ExpenseViewSet)
router.register("audit-entries", AuditEntryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
