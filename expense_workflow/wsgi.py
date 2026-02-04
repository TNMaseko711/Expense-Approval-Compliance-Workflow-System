"""WSGI config for the Expense Approval & Compliance Workflow System."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_workflow.settings")

application = get_wsgi_application()
