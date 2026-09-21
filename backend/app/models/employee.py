"""
models/employee.py
------------------
Pydantic models for employee-related data.
"""

from typing import Optional
from pydantic import BaseModel, Field


class Employee(BaseModel):
    """Represents a single employee record."""
    employee_id: str
    name: str
    department: str
    position: str
    email: str
    leave_balance: int = Field(..., ge=0, description="Remaining leave days")
    manager: Optional[str] = None


class LeaveRequest(BaseModel):
    """Represents a submitted leave request (stored in leave_requests.json)."""
    request_id: str
    employee_id: str
    start_date: str   # ISO date string "YYYY-MM-DD"
    end_date: str     # ISO date string "YYYY-MM-DD"
    days: int
    reason: str
    status: str = "pending"  # pending | approved | rejected


class LeaveApplicationResult(BaseModel):
    """Result returned to the agent after apply_leave runs."""
    status: str          # "success" or "error"
    message: str
    employee_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days: Optional[int] = None
    remaining_balance: Optional[int] = None
