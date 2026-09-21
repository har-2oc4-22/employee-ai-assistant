"""
tools/apply_leave.py
---------------------
Tool 3: apply_leave

Yeh tool tab call hota hai jab user employee portal se chhutti (leave) apply karta hai.

SECURITY & ARCHITECTURE RULE (Hinglish me samjhein):
  - LLM seedhe database ya JSON file ko change nahi kar sakta.
  - LLM sirf 'Decision Maker' hai — wo decide karta hai ki user ke bolne par kab tool chalana hai.
  - Asli checking (Dates valid hain ya nahi, balance bacha hai ya nahi, balance deduct karna)
    sab Python code (employee_service.py) me safely execute hota hai.
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
    Submit a leave request for an employee.

    Yeh tool kya karta hai:
    1. Employee ID check karta hai ki employee exist karta hai ya nahi.
    2. Start date aur end date ka range check karta hai (end date pehle nahi honi chahiye).
    3. Working days count karta hai.
    4. Check karta hai ki employee ke paas utna leave balance available hai ya nahi.
    5. Agar balance hai, toh request submit karke balance deduct karta hai.

    Args:
        employee_id: Employee ID, jaise "EMP001"
        start_date:  Chhutti shuru hone ki date (YYYY-MM-DD), jaise "2026-10-06"
        end_date:    Chhutti khatam hone ki date (YYYY-MM-DD), jaise "2026-10-07"
        reason:      Leave lene ki wajah (reason)

    Returns:
        JSON string: success confirmation ke sath, ya error message kyu reject hua uske reason ke sath.
    """
    logger.info(
        "apply_leave tool call hua | emp=%s, %s se %s tak, reason='%s'",
        employee_id, start_date, end_date, reason,
    )

    try:
        # Business logic function ko call karte hain jo database update karta hai
        result = _apply_leave(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

        output = result.model_dump()
        logger.info(
            "apply_leave ka result aaya → status=%s, msg='%s'",
            result.status, result.message,
        )
        return json.dumps(output)

    except Exception as e:
        logger.error("apply_leave tool me exception aaya: %s", e, exc_info=True)
        return json.dumps({
            "status": "error",
            "message": "An unexpected error occurred while applying leave. Please try again.",
        })
