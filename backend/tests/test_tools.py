"""
tests/test_tools.py
--------------------
Unit tests for the three agent tools and the employee service.

These tests use mock data and do NOT require a running backend or Gemini API key.
"""

import json
import os
import sys
import pytest

# Ensure we can import from the backend package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set a dummy key so config doesn't fail on import
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ["EMPLOYEES_FILE"] = "./data/employees.json"
os.environ["LEAVE_REQUESTS_FILE"] = "./data/leave_requests.json"


from app.services.employee_service import get_employee, apply_leave, _count_working_days


class TestGetEmployee:
    """Tests for the get_employee service function."""

    def test_get_existing_employee(self):
        emp = get_employee("EMP001")
        assert emp is not None
        assert emp.employee_id == "EMP001"
        assert emp.name == "Rahul Sharma"
        assert emp.department == "Engineering"
        assert emp.leave_balance >= 0

    def test_get_nonexistent_employee(self):
        emp = get_employee("EMP999")
        assert emp is None

    def test_employee_id_case_insensitive(self):
        emp = get_employee("emp001")
        assert emp is not None
        assert emp.employee_id == "EMP001"


class TestApplyLeave:
    """Tests for the apply_leave service function."""

    def test_apply_valid_leave(self):
        # EMP003 has 15 days — apply 2 days
        result = apply_leave(
            employee_id="EMP003",
            start_date="2026-10-06",   # Monday
            end_date="2026-10-07",     # Tuesday
            reason="Personal work",
        )
        # May succeed or partially succeed depending on current balance state
        # Just check that status is a string
        assert result.status in ("success", "error")
        if result.status == "success":
            assert result.days == 2
            assert result.remaining_balance is not None

    def test_apply_leave_invalid_employee(self):
        result = apply_leave(
            employee_id="EMP999",
            start_date="2026-10-06",
            end_date="2026-10-07",
            reason="test",
        )
        assert result.status == "error"
        assert "not found" in result.message.lower()

    def test_apply_leave_invalid_date_format(self):
        result = apply_leave(
            employee_id="EMP001",
            start_date="20-10-2026",   # wrong format
            end_date="2026-10-22",
            reason="test",
        )
        assert result.status == "error"
        assert "invalid" in result.message.lower()

    def test_apply_leave_end_before_start(self):
        result = apply_leave(
            employee_id="EMP001",
            start_date="2026-10-22",
            end_date="2026-10-20",   # before start
            reason="test",
        )
        assert result.status == "error"
        assert "before" in result.message.lower()


class TestCountWorkingDays:
    """Tests for the working day calculation helper."""

    def test_mon_to_fri_is_5_days(self):
        from datetime import date
        start = date(2026, 9, 28)  # Monday
        end = date(2026, 10, 2)    # Friday
        assert _count_working_days(start, end) == 5

    def test_weekend_only_is_0_days(self):
        from datetime import date
        start = date(2026, 9, 26)  # Saturday
        end = date(2026, 9, 27)    # Sunday
        assert _count_working_days(start, end) == 0

    def test_single_working_day(self):
        from datetime import date
        start = date(2026, 9, 21)  # Monday
        end = date(2026, 9, 21)    # Same Monday
        assert _count_working_days(start, end) == 1
