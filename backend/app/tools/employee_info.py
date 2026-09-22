"""
tools/employee_info.py
-----------------------
Tool 2: get_employee_info

The agent calls this tool to look up employee details
(name, department, leave balance, etc.).

SECURITY NOTE:
  This tool only READS data. It cannot modify the employee record.
  Only apply_leave can modify leave_balance.
"""

import json
import logging

from langchain_core.tools import tool

from app.services.employee_service import get_employee

logger = logging.getLogger(__name__)


@tool
def get_employee_info(employee_id: str) -> str:
    """
    Retrieve information about an EnWIDTH Technologies employee by their employee ID.

    Use this tool whenever the user asks about:
    - Their own leave balance ("How many leaves do I have?")
    - Employee details (name, department, position)
    - Before applying leave (to verify identity and check balance)

    Args:
        employee_id: The employee ID string, e.g. "EMP001"

    Returns:
        JSON string with employee details, or an error message if not found.
    """
    logger.info("Tool: get_employee_info | Employee ID: '%s'", employee_id)

    try:
        emp_id = employee_id.strip().upper()
        employee = get_employee(emp_id)

        if not employee:
            result = {
                "found": False,
                "error": f"Employee ID '{emp_id}' was not found in the system. "
                         "Please check the employee ID and try again.",
            }
            logger.warning("Employee not found: '%s'", emp_id)
            return json.dumps(result)

        result = {
            "found": True,
            "employee_id": employee.employee_id,
            "name": employee.name,
            "department": employee.department,
            "position": employee.position,
            "email": employee.email,
            "leave_balance": employee.leave_balance,
            "manager": employee.manager,
        }

        logger.info(
            "Tool: get_employee_info → %s (%s), balance=%d",
            employee.name,
            employee.employee_id,
            employee.leave_balance,
        )
        return json.dumps(result)

    except Exception as e:
        logger.error("Error in get_employee_info: %s", e, exc_info=True)
        return json.dumps({
            "found": False,
            "error": "Failed to retrieve employee information. Please try again.",
        })
