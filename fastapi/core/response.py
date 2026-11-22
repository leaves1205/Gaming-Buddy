"""
Shared response builders

- Standard responses use {code, msg, ...} with code 200 for success and 500 for failure. HTTP status is always 200.
- Paginated responses use {total, rows, code, msg}
- Pass extra fields as keyword arguments
"""
from typing import Any  # Standard-library Any type


def ajax_success(msg: str = "Operation successful", **extra: Any) -> dict:
    r = {"code": 200, "msg": msg}  # Base success response
    r.update(extra)  # Merge extra keyword fields such as token
    return r


def ajax_success_data(data: Any, msg: str = "Operation successful", **extra: Any) -> dict:
    r = {"code": 200, "msg": msg}  # Base success response
    if data is not None:  # Include data only when it is non-null
        r["data"] = data
    r.update(extra)  # Merge extra keyword fields
    return r


def ajax_error(msg: str = "Operation failed", **extra: Any) -> dict:
    r = {"code": 500, "msg": msg}  # The HTTP status remains 200. The frontend uses code to determine the message.
    r.update(extra)  # Merge extra keyword fields
    return r


def to_ajax(rows: int, msg: str = "Operation successful") -> dict:
    """Check the database affected row count to determine success"""
    return ajax_success(msg) if rows > 0 else ajax_error()  # A positive affected row count indicates success


def page_data(rows: list, total: int, msg: str = "List retrieved successfully") -> dict:
    """Paginated list response"""
    return {"total": total, "rows": rows, "code": 200, "msg": msg}  # The frontend table expects the total and the current page of rows
