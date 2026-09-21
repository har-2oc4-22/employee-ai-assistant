"""
tools/__init__.py
-----------------
Exports all three agent tools so the agent can import them from one place.
"""
from .knowledge_search import search_company_documents
from .employee_info import get_employee_info
from .apply_leave import apply_leave

ALL_TOOLS = [search_company_documents, get_employee_info, apply_leave]

__all__ = [
    "search_company_documents",
    "get_employee_info",
    "apply_leave",
    "ALL_TOOLS",
]
