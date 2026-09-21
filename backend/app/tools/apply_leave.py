"""
tools/apply_leave.py
---------------------
Tool 3: apply_leave

The agent calls this tool to submit a leave request on behalf of an employee.

CRITICAL DESIGN RULE:
  The LLM cannot directly modify data. All validation and mutation happens
  in employee_service.py (Python code). The LLM only decides WHEN to call
  this tool — never HOW the data changes.

  This is the safest architecture: the LLM is the decision-maker,
  Python is the executor.
"""

import json
import logging

from langchain_core.tools import tool

from app.services.employee_service import apply_leave as _apply_leave

logger = logging.getLogger(__name__)


@tool
def apply_leave(
    employee_id: str,
    start_date: str,
    end_date: str,
    reason: str,
) -> str:
    """
    Submit a leave request for a TechCorp employee.

    This tool:
    1. Validates the employee ID.
    2. Validates the date range.
    3. Calculates the number of working days requested.
    4. Checks whether the employee has enough leave balance.
    5. If valid, submits the request and deducts the balance.

    IMPORTANT: Always call get_employee_info BEFORE calling this tool
    to verify the employee exists and check their current leave balance.

    Args:
        employee_id: Employee ID, e.g. "EMP001"
        start_date:  Leave start date in YYYY-MM-DD format, e.g. "2026-09-20"
        end_date:    Leave end date in YYYY-MM-DD format, e.g. "2026-09-22"
        reason:      Reason for the leave request

    Returns:
        JSON string with the result: success (with confirmation) or error (with reason).
    """
    logger.info(
        "Tool: apply_leave | emp=%s, %s to %s, reason='%s'",
        employee_id, start_date, end_date, reason,
    )

    try:
        result = _apply_leave(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

        output = result.model_dump()
        logger.info(
            "Tool: apply_leave result → status=%s, msg='%s'",
            result.status, result.message,
        )
        return json.dumps(output)

    except Exception as e:
        logger.error("Error in apply_leave tool: %s", e, exc_info=True)
        return json.dumps({
            "status": "error",
            "message": "An unexpected error occurred while applying leave. Please try again.",
        })
