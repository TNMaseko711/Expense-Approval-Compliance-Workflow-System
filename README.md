# Expense Approval & Compliance Workflow System

## Overview
This project demonstrates modeling a **business process** (expense submission → approval → rejection → audit), not just data. The workflow is enforced as a backend state machine to ensure compliance, auditability, and correct business outcomes even if a client attempts invalid transitions.

## Domain framing
1. **Expense submission**
2. **Approval**
3. **Rejection**
4. **Audit** (immutable trail)

## Tech stack
- **Backend:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Frontend:** React *or* simple Django templates

## Core functionality
- Submit expense requests with attachments
- Approval hierarchy: **Employee → Manager → Finance**
- Status transitions enforced server-side
- Rejection reasons are mandatory
- Immutable audit trail (no edits after approval)

## Critical business rules
- Expenses above a threshold **require Finance approval**
- **Approved expenses cannot be modified**
- **Rejected expenses can be resubmitted** (new submission with a new audit entry)

## Workflow enforcement (state transitions)
The backend implements a strict state machine. Every transition is validated on the server to prevent invalid workflow jumps and to preserve audit integrity.

### Example states
- `draft`
- `submitted`
- `manager_approved`
- `finance_approved`
- `rejected`

### Example transition rules
- `draft → submitted` (employee submits)
- `submitted → manager_approved` (manager approves)
- `manager_approved → finance_approved` (finance approves for high-value expenses)
- `submitted → rejected` or `manager_approved → rejected` (rejection requires a reason)
- Any attempt to skip directly to `finance_approved` is rejected by the API.

## How state transitions are enforced
All transitions are validated in the **backend service layer** or model methods. The API refuses invalid transitions even if a client tries to bypass UI constraints. Each transition:
- Checks current status
- Validates the user role (employee/manager/finance)
- Enforces required fields (e.g., rejection reason)
- Records an audit entry

## Preventing invalid workflow jumps
Invalid transitions are blocked in server-side logic (e.g., Django model methods, serializers, or service classes). This ensures:
- No direct jump from `submitted` to `finance_approved` unless manager approval exists
- No edits once `finance_approved` is reached
- No approval actions by unauthorized roles

## Why business rules live in the backend
Business rules are enforced server-side because:
- **Security:** Clients can be manipulated; server must be the source of truth.
- **Consistency:** Every client (UI, mobile, API integration) must follow the same rules.
- **Auditability:** Backend enforcement guarantees a reliable, immutable audit trail.
- **Compliance:** Regulatory and policy requirements demand strict control.

## Recruiter signal
This project highlights state-machine thinking: transitions are explicit, validated, and audited—demonstrating real-world workflow modeling.

## Running locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Apply migrations:
   ```bash
   python manage.py migrate
   ```
3. Create a user and group roles:
   ```bash
   python manage.py createsuperuser
   ```
4. Start the server:
   ```bash
   python manage.py runserver
   ```

## API usage (high-level)
### Submit a draft for approval
```http
POST /api/expenses/{id}/transition
{
  "target_status": "submitted"
}
```

### Manager approval
```http
POST /api/expenses/{id}/transition
{
  "target_status": "manager_approved"
}
```

### Finance approval (only if amount >= threshold)
```http
POST /api/expenses/{id}/transition
{
  "target_status": "finance_approved"
}
```

### Rejection (reason required)
```http
POST /api/expenses/{id}/transition
{
  "target_status": "rejected",
  "reason": "Missing receipt"
}
```
