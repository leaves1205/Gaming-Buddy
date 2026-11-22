"""
Role service

insert_role and update_role write to role and role_menu in one atomic transaction.
"""
# SQLAlchemy delete and update expressions for the update_role transaction
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session  # Session type annotation

from core.common import (  # Shared utilities
    body_fields, delete_by_pks, eq_if, like_if, paginate, row_to_dict, where_if,
)
from models.entities import Role, RoleMenu  # Role and role-menu ORM entities
from schemas.body import RoleBody  # Role request model

_ROLE_COLS = (Role.role_id, Role.role_name, Role.role_sort, Role.remark, Role.create_time)  # Selected role columns


def role_row_to_dict(row) -> dict:
    """Convert the database row to a camelCase dictionary"""
    return row_to_dict(row, {"menuIds": None})  # Populate the menuIds placeholder separately as needed


def _base_query(role_id: int | None, role_name: str | None):
    """Build a reusable role query with dynamic filters"""
    stmt = select(*_ROLE_COLS)  # Select role columns
    stmt = where_if(stmt, eq_if(Role.role_id, role_id), like_if(Role.role_name, role_name))  # Add filters for populated values
    return stmt.order_by(Role.role_sort)  # Sort by display order


def select_role_list(db: Session, role_id: int | None = None,
                     role_name: str | None = None) -> list[dict]:
    """List roles without pagination, sorted by role_sort"""
    rows = db.execute(_base_query(role_id, role_name)).all()  # Execute the query and fetch all rows
    return [role_row_to_dict(r) for r in rows]  # Convert to a list of camelCase dictionaries


def select_role_page(db: Session, page_num: int, page_size: int,
                     role_id: int | None = None, role_name: str | None = None) -> tuple[int, list[dict]]:
    stmt = _base_query(role_id, role_name)  # Reuse the base query
    total, rows = paginate(db, stmt, page_num, page_size)  # Paginate with count and offset/limit
    return total, [role_row_to_dict(r) for r in rows]  # Return the total and current page of dictionaries


def get_role_by_id(db: Session, role_id: int) -> dict | None:
    row = db.execute(select(*_ROLE_COLS).where(Role.role_id == role_id)).first()  # Fetch the first matching row
    return role_row_to_dict(row) if row else None  # Return None if no record exists


def insert_role(db: Session, body: RoleBody) -> int:
    """Create the role and its menu assignments in one transaction"""
    role = Role(**body_fields(body, skip=("roleId", "menuIds")))  # Create the role entity from the request fields
    db.add(role)  # Add to the session before committing
    db.flush()  # Populate the generated primary key
    rows = 1  # The role itself accounts for one affected row by default
    if body.menuIds:  # A list of assigned menus was provided
        db.add_all([RoleMenu(role_id=role.role_id, menu_id=mid) for mid in body.menuIds])  # Build role-menu associations in bulk
        rows = len(body.menuIds)  # Use the association count as the affected row count
    db.commit()  # Commit role and role_menu together
    return rows


def update_role(db: Session, body: RoleBody) -> int:
    """Update the role and replace menu associations in one transaction

    None preserves existing assignments. An empty list clears all assignments.
    """
    if body.roleId is None:  # The primary key is required to find the record
        return 0
    fields = body_fields(body, skip=("roleId", "menuIds"))  # Extract non-null fields
    if not fields and body.menuIds is None:  # Skip when both update fields and assignments are omitted
        return 0
    if fields:  # Run the update only if there are fields to write
        db.execute(update(Role).where(Role.role_id == body.roleId).values(**fields))  # Update the role record
    rows = 1  # The role itself accounts for one affected row by default
    if body.menuIds is not None:  # Replace assignments only if supplied. None preserves and [] clears.
        db.execute(delete(RoleMenu).where(RoleMenu.role_id == body.roleId))  # Delete existing role-menu associations
        if body.menuIds:  # A list of assigned menus was provided
            db.add_all([RoleMenu(role_id=body.roleId, menu_id=mid) for mid in body.menuIds])  # Insert the new associations
            rows = len(body.menuIds)  # Use the association count as the affected row count
    db.commit()  # Commit the update, deletions and insertions together
    return rows


def delete_role_by_ids(db: Session, role_ids: list[int]) -> int:
    """Delete roles. ON DELETE CASCADE removes associated role_menu entries."""
    return delete_by_pks(db, Role, Role.role_id, role_ids)  # Use the shared bulk deletion helper
