"""ASGI config for the Expense Approval & Compliance Workflow System."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_workflow.settings")

application = get_asgi_application()
