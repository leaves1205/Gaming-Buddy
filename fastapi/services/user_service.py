"""
User service

Join the role table for role_name when listing or retrieving users.
"""
# SQLAlchemy query and count expressions and unique constraint exceptions
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session  # Session type annotation

from core.common import (  # Shared utilities
    body_fields, delete_by_pks, eq_if, insert_row, like_if, paginate, row_to_dict, update_by_pk, where_if,
)
from models.entities import Role, User  # User and role ORM entities
from schemas.body import UserBody  # User request model

# Select user columns and role_name. Exclude passwords from API responses.
_USER_COLS = (  # Column order matches row_to_dict keys
    User.user_id, User.user_name, User.sex, User.avatar,
    User.create_time, User.role_id, Role.role_name,
)


def user_row_to_dict(row) -> dict:
    """Convert the database row to a camelCase dictionary"""
    return row_to_dict(row)  # Use the shared conversion directly because there are no placeholders


def get_user_by_name(db: Session, user_name: str) -> User | None:
    """Get a user by username and return all columns"""
    return db.scalar(select(User).where(User.user_name == user_name))  # Fetch the full row by username or return None


def get_user_password(db: Session, user_id: int) -> str | None:
    """Get the password by ID for password checks. Keep it out of API responses."""
    return db.scalar(select(User.password).where(User.user_id == user_id))


def get_user_avatar(db: Session, user_id: int) -> str | None:
    """Get the avatar URL by ID for cleanup after replacement"""
    return db.scalar(select(User.avatar).where(User.user_id == user_id))


def user_name_taken(db: Session, user_name: str, exclude_user_id: int | None = None) -> bool:
    """Check if a username is taken. exclude_user_id excludes the account being renamed."""
    stmt = select(User.user_id).where(User.user_name == user_name)
    if exclude_user_id is not None:  # Exclude the current account from duplicate checks when renaming it
        stmt = stmt.where(User.user_id != exclude_user_id)
    return db.scalar(stmt) is not None


def get_user_by_id(db: Session, user_id: int) -> dict | None:
    """Get a user by ID and left join role for role_name"""
    stmt = (  # Use a left join to retain users without a role
        select(*_USER_COLS)
        .join(Role, User.role_id == Role.role_id, isouter=True)
        .where(User.user_id == user_id)
    )
    row = db.execute(stmt).first()  # Get the first row. A primary key matches at most one row.
    return user_row_to_dict(row) if row else None  # Return None if no record exists


def register_user(db: Session, user_name: str, password: str) -> bool:
    """Register a user. Return False for duplicates so the route can return HTTP 200 with code 500."""
    if get_user_by_name(db, user_name) is not None:  # This username is already taken
        return False
    try:  # New users default to role_id=2. The unique index handles concurrent duplicate registrations.
        db.add(User(user_name=user_name, password=password))
        db.commit()  # Commit the single-table write immediately
    except IntegrityError:  # The unique constraint on user_name was violated
        db.rollback()  # Roll back to keep the session usable
        return False
    return True


def page_users(db: Session, page_num: int, page_size: int,
               user_id: int | None, user_name: str | None) -> tuple[int, list[dict]]:
    """Get a paginated list of users"""
    stmt = select(*_USER_COLS).join(Role, User.role_id == Role.role_id, isouter=True)  # Select user columns and left join the role name
    stmt = where_if(stmt, eq_if(User.user_id, user_id), like_if(User.user_name, user_name))  # Add filters for populated values
    stmt = stmt.order_by(User.user_id)  # Sort by ID
    total, rows = paginate(db, stmt, page_num, page_size)  # Paginate with count and offset/limit
    return total, [user_row_to_dict(r) for r in rows]  # Return the total and current page of camelCase dictionaries


def insert_user(db: Session, body: UserBody) -> int:
    """Insert non-null fields. The database generates the ID and creation time."""
    fields = body_fields(body, skip=("userId", "createTime"))  # Convert the request body to database columns and omit createTime
    return insert_row(db, User, fields)  # Insert and commit with the shared single-table helper


def update_user_by_id(db: Session, user_id: int, fields: dict) -> int:
    """Update non-null fields keyed by database column name"""
    return update_by_pk(db, User, User.user_id, user_id, fields)  # Use the shared dynamic update helper


def reset_user_pwd(db: Session, user_id: int, new_password: str) -> int:
    return update_by_pk(db, User, User.user_id, user_id, {"password": new_password})  # Update the password by primary key


def update_user_avatar(db: Session, user_id: int, avatar: str) -> int:
    return update_by_pk(db, User, User.user_id, user_id, {"avatar": avatar})  # Update the avatar URL by primary key


def delete_user_by_ids(db: Session, user_ids: list[int]) -> int:
    """Delete users. ON DELETE CASCADE cleans up their associated records."""
    return delete_by_pks(db, User, User.user_id, user_ids)  # Use the shared bulk deletion helper


def count_admins_except(db: Session, exclude_ids: list[int]) -> int:
    """Count the administrators remaining after the proposed deletion"""
    stmt = select(func.count()).select_from(User).where(User.role_id == 1)  # role_id=1 identifies administrators
    if exclude_ids:  # Exclude the users being deleted
        stmt = stmt.where(User.user_id.not_in(exclude_ids))
    return db.scalar(stmt) or 0
