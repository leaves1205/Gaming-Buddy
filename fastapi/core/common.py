"""
Shared utilities

Alongside date helpers, this module contains utilities shared by feature modules.
- Key conversion with snake_to_camel and camel_to_snake
- Row conversion with row_to_dict, from database rows to camelCase dictionaries
- Request conversion with body_fields, from request bodies to non-null database columns
- Filter factories eq_if, like_if and between_if skip empty values. where_if combines the filters.
- Pagination and CRUD with paginate, insert_row, update_by_pk and delete_by_pks
- Route helper split_ids parses deletion path parameters such as "1,2,3"

Reuse these functions in new feature modules and keep service code specific to the feature.
"""
import re  # Standard-library regex support for camelCase keys
from datetime import datetime  # Standard-library date and time types and parsing

from pydantic import BaseModel  # Request body base model for type annotations
from sqlalchemy import delete, func, select, update  # Shared CRUD and count expressions
from sqlalchemy.orm import Session  # Session type annotation

# Shared date output format
DT_FORMAT = "%Y-%m-%d %H:%M:%S"


def fmt_dt(value) -> str | None:
    """Format a datetime as 'yyyy-MM-dd HH:mm:ss'"""
    if value is None:  # Return null values unchanged
        return None
    if isinstance(value, str):  # Strings already have the expected format
        return value
    return value.strftime(DT_FORMAT)  # Format datetimes consistently


def parse_dt(value: str | None) -> datetime | None:
    """Parse 'yyyy-MM-dd HH:mm:ss' as a datetime, or return None on failure"""
    if not value:  # Skip empty strings and None
        return None
    for pattern in (DT_FORMAT, "%Y-%m-%d"):  # Try the full datetime format first, then the date-only format
        try:
            return datetime.strptime(value, pattern)  # Return the first successful match
        except ValueError:
            continue  # Try the next format if this one fails
    return None  # Return None if every format fails


# ==================== Key conversion ====================

def snake_to_camel(key: str) -> str:
    """snake_case -> camelCase(user_name -> userName)"""
    head, *rest = key.split("_")  # Split on underscores and keep the first segment as is
    return head + "".join(w.capitalize() for w in rest)  # Join the first segment with the capitalized remaining segments


def camel_to_snake(key: str) -> str:
    """camelCase -> snake_case(userName -> user_name)"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()  # Insert underscores before uppercase letters after the first character, then lowercase


# ==================== Row and request conversion ====================

def row_to_dict(row, extra: dict | None = None) -> dict:
    """Convert a database row to a camelCase dictionary and format all datetime values

    Use extra for placeholder fields or computed join columns such as role menuIds or menu children.
    """
    d: dict = {}  # Result dictionary
    for k, v in dict(row._mapping).items():  # Iterate over the row's column-to-value mapping
        d[snake_to_camel(k)] = fmt_dt(v) if isinstance(v, datetime) else v  # Convert keys to camelCase and format datetimes consistently
    if extra:  # Merge additional fields without overwriting converted columns
        d.update(extra)
    return d


# Request body fields whose string values are parsed as datetimes. Register new date fields here.
_DATE_FIELDS = {"createTime", "updateTime"}


def body_fields(body: BaseModel, skip: tuple = ()) -> dict:
    """Convert a Pydantic request body to non-null database columns with snake_case keys

    Set skip to fields excluded from database writes, such as primary keys and menuIds.
    """
    fields: dict = {}  # Result dictionary
    for key, value in body.model_dump(exclude_none=True).items():  # Iterate over non-null fields only
        if key in skip:  # Skip primary keys and other fields excluded from database writes
            continue
        if key in _DATE_FIELDS:  # Parse date fields from strings into datetimes
            dt = parse_dt(value)  # Return None if parsing fails
            if dt is not None:  # Write only successfully parsed values
                fields[camel_to_snake(key)] = dt
        else:
            fields[camel_to_snake(key)] = value  # Convert other keys to snake_case and keep their values
    return fields


# ==================== Query filter factories ====================

def eq_if(col, value):
    """Build an equality filter for a non-None value, or return None for callers to filter out"""
    return col == value if value is not None else None


def like_if(col, value: str | None):
    """Build a LIKE filter for a nonempty string, or return None for callers to filter out"""
    return col.like(f"%{value}%") if value else None


def between_if(col, begin, end):
    """Build an inclusive range when at least one bound is supplied, or return None

    Use for date filters such as createTime between '2026-01-01' and '2026-12-31'.
    Supplying only begin sets the lower bound. Supplying only end sets the upper bound.
    """
    if begin is None and end is None:  # Skip the range filter when both bounds are empty
        return None
    return col.between(begin, end)  # SQLAlchemy between treats None bounds as open


def where_if(stmt, *conds):
    """Combine non-None filters in a WHERE clause, or return stmt unchanged

    Combine dynamic filters from eq_if, like_if and between_if in one call
        stmt = where_if(stmt, eq_if(User.user_id, user_id), like_if(User.user_name, user_name))
    """
    valid = [c for c in conds if c is not None]  # Keep only non-None conditions
    return stmt.where(*valid) if valid else stmt  # Add WHERE only when conditions exist


# ==================== Shared pagination and CRUD ====================

def paginate(db: Session, stmt, page_num: int, page_size: int) -> tuple[int, list]:
    """Paginate with a count and offset/limit. Return the total and the rows on the current page.

    Pass a stmt with its joins, filters and ordering already applied. Counting drops the ordering.
    Clamp the page to at least 1 and the page size to 1–500 to prevent negative offsets and excessive memory use.
    """
    page_num = max(1, page_num)  # Clamp the page because zero or negative values produce invalid SQL offsets
    page_size = min(max(1, page_size), 500)  # Clamp pageSize to 1–500 to limit database load
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0  # Drop the ordering before counting the subquery
    rows = db.execute(stmt.offset((page_num - 1) * page_size).limit(page_size)).all()  # Skip the first (page number - 1) * page size rows
    return total, list(rows)


def insert_row(db: Session, model, fields: dict) -> int:
    """Insert and commit one row, then return the affected row count. Use a separate transaction for multi-table writes."""
    db.add(model(**fields))  # Create the entity and add it to the session
    db.commit()  # Commit the single-table write immediately
    return 1


def update_by_pk(db: Session, model, pk_col, pk_value, fields: dict) -> int:
    """Update non-null fields by primary key, commit and return the affected row count"""
    fields = {k: v for k, v in fields.items() if v is not None}  # Skip null fields
    if not fields:  # Return immediately if there are no fields to update
        return 0
    result = db.execute(update(model).where(pk_col == pk_value).values(**fields))  # Update non-null columns by primary key
    db.commit()  # Commit the transaction
    return result.rowcount


def delete_by_pks(db: Session, model, pk_col, ids: list) -> int:
    """Delete by primary key in bulk, commit and return the affected row count"""
    result = db.execute(delete(model).where(pk_col.in_(ids)))  # Delete in bulk by ID
    db.commit()  # Commit the transaction
    return result.rowcount


# ==================== Route helpers ====================

def split_ids(raw: str) -> list[int]:
    """Parse a deletion path parameter such as "1,2,3" into [1, 2, 3]

    Allow empty input and extra commas. Non-numeric segments raise ValueError for the global handler.
    """
    return [int(x) for x in raw.split(",") if x.strip()]  # Trim each segment and convert it to an integer
