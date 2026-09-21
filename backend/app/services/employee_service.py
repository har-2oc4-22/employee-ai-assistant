"""
services/employee_service.py
------------------------------
Business logic for employee data access and leave management.

WHY A SERVICE LAYER?
  Tools call these functions. Business logic (date validation, balance checks)
  lives here — not in the agent, not in the LLM. This ensures:
  - The LLM cannot bypass validation.
  - Business rules are easy to test independently.
  - Swapping JSON → PostgreSQL only requires changing this file.
"""

import json
import logging
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

from app.config import settings
from app.models.employee import Employee, LeaveApplicationResult, LeaveRequest

logger = logging.getLogger(__name__)


def _load_employees() -> Dict[str, dict]:
    """Load the employees JSON file into memory."""
    path = Path(settings.EMPLOYEES_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Employees file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_employees(data: Dict[str, dict]) -> None:
    """Persist updated employee data back to the JSON file."""
    path = Path(settings.EMPLOYEES_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _load_leave_requests() -> list:
    """Load existing leave requests from JSON."""
    path = Path(settings.LEAVE_REQUESTS_FILE)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_leave_requests(requests: list) -> None:
    """Persist leave requests back to JSON."""
    path = Path(settings.LEAVE_REQUESTS_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(requests, f, indent=2, default=str)


# ── Public API ─────────────────────────────────────────────────────────────

def get_employee(employee_id: str) -> Optional[Employee]:
    """
    Fetch a single employee record by ID.
    Returns None if employee_id does not exist.
    """
    employees = _load_employees()
    data = employees.get(employee_id.upper())
    if not data:
        return None
    return Employee(**data)


def apply_leave(
    employee_id: str,
    start_date: str,
    end_date: str,
    reason: str,
) -> LeaveApplicationResult:
    """
    Validate and submit a leave request.

    Validation steps:
    1. Employee must exist.
    2. Dates must be valid ISO format (YYYY-MM-DD).
    3. start_date must be <= end_date.
    4. Requested days must not exceed leave_balance.

    If all validations pass:
    - Deduct leave_balance in the employees JSON.
    - Store a leave request record in leave_requests JSON.
    - Return a success result.

    NOTE: The LLM never calls this function directly.
          It goes through the apply_leave tool, which enforces this logic.
    """
    emp_id = employee_id.upper()
    employees = _load_employees()

    # 1. Validate employee
    if emp_id not in employees:
        return LeaveApplicationResult(
            status="error",
            message=f"Employee ID '{emp_id}' not found. Please check your employee ID.",
        )

    employee = employees[emp_id]

    # 2. Validate dates
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        return LeaveApplicationResult(
            status="error",
            message=f"Invalid start date '{start_date}'. Please use YYYY-MM-DD format.",
        )

    try:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return LeaveApplicationResult(
            status="error",
            message=f"Invalid end date '{end_date}'. Please use YYYY-MM-DD format.",
        )

    # 3. end must be >= start
    if end < start:
        return LeaveApplicationResult(
            status="error",
            message=f"End date ({end_date}) cannot be before start date ({start_date}).",
        )

    # 4. Calculate working days (Mon–Fri only, no holiday check for simplicity)
    requested_days = _count_working_days(start, end)

    if requested_days == 0:
        return LeaveApplicationResult(
            status="error",
            message="The selected dates contain no working days (weekends only).",
        )

    # 5. Check leave balance
    current_balance = employee["leave_balance"]
    if requested_days > current_balance:
        return LeaveApplicationResult(
            status="error",
            message=(
                f"Insufficient leave balance. "
                f"You requested {requested_days} day(s) but only have {current_balance} day(s) remaining."
            ),
        )

    # 6. Submit — deduct balance
    new_balance = current_balance - requested_days
    employees[emp_id]["leave_balance"] = new_balance
    _save_employees(employees)

    # 7. Record the leave request
    leave_record = {
        "request_id": str(uuid.uuid4()),
        "employee_id": emp_id,
        "employee_name": employee["name"],
        "start_date": start_date,
        "end_date": end_date,
        "days": requested_days,
        "reason": reason,
        "status": "approved",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    requests = _load_leave_requests()
    requests.append(leave_record)
    _save_leave_requests(requests)

    logger.info(
        "Leave approved: emp=%s, %s to %s, days=%d, remaining=%d",
        emp_id, start_date, end_date, requested_days, new_balance,
    )

    return LeaveApplicationResult(
        status="success",
        message="Leave application submitted and approved successfully.",
        employee_id=emp_id,
        start_date=start_date,
        end_date=end_date,
        days=requested_days,
        remaining_balance=new_balance,
    )


def _count_working_days(start: date, end: date) -> int:
    """
    Count the number of Monday–Friday days between start and end (inclusive).
    Weekends are excluded. Public holidays are not checked (simplification for assessment).
    """
    count = 0
    current = start
    while current <= end:
        if current.weekday() < 5:  # 0=Mon, 4=Fri
            count += 1
        current += timedelta(days=1)
    return count
