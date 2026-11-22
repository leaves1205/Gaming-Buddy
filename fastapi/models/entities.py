"""
ORM entities matching the table schemas in fast.sql
"""
from datetime import datetime  # Standard-library datetime type

# SQLAlchemy column types and database functions
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column  # SQLAlchemy 2.0 typed declarative mappings

from core.database import Base  # Application ORM base class


class User(Base):
    """User table"""
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column("user_id", Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    user_name: Mapped[str] = mapped_column("user_name", String(50))  # Username. The service checks for duplicates.
    sex: Mapped[int | None] = mapped_column("sex", Integer, nullable=True)  # Optional gender
    avatar: Mapped[str | None] = mapped_column("avatar", String(255), nullable=True)  # Optional avatar URL
    password: Mapped[str] = mapped_column("password", String(255))  # Password stored as plain text
    role_id: Mapped[int] = mapped_column("role_id", Integer, nullable=False, server_default="2")  # Role ID, defaulting to 2 (regular user)
    balance: Mapped[int] = mapped_column("balance", Integer, nullable=False, server_default="0")
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # Creation time, defaulting to the database time


class Role(Base):
    """Role table"""
    __tablename__ = "role"

    role_id: Mapped[int] = mapped_column("role_id", Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    role_name: Mapped[str] = mapped_column("role_name", String(255))  # Role name
    role_sort: Mapped[int] = mapped_column("role_sort", Integer, nullable=False)  # Display order
    remark: Mapped[str | None] = mapped_column("remark", String(500), nullable=True)  # Optional notes
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # Creation time, defaulting to the database time


class Menu(Base):
    """Menu table"""
    __tablename__ = "menu"

    menu_id: Mapped[int] = mapped_column("menu_id", Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    menu_name: Mapped[str] = mapped_column("menu_name", String(100))  # Menu name
    parent_id: Mapped[int | None] = mapped_column("parent_id", Integer, nullable=True, server_default="0")  # Parent menu ID (0 for top level)
    menu_sort: Mapped[int] = mapped_column("menu_sort", Integer, nullable=False)  # Display order
    path: Mapped[str | None] = mapped_column("path", String(255), nullable=True)  # Optional route path
    component: Mapped[str | None] = mapped_column("component", String(255), nullable=True)  # Optional component path
    menu_type: Mapped[str] = mapped_column("menu_type", String(10))  # Menu type (M for directory, C for menu item)
    icon: Mapped[str | None] = mapped_column("icon", String(100), nullable=True)  # Optional icon name
    create_time: Mapped[datetime | None] = mapped_column(
        "create_time", DateTime, server_default=func.now()
    )  # Creation time, defaulting to the database time


class RoleMenu(Base):
    """Role-menu association table"""
    __tablename__ = "role_menu"

    role_id: Mapped[int] = mapped_column("role_id", Integer, primary_key=True)  # Role ID (part of the composite primary key)
    menu_id: Mapped[int] = mapped_column("menu_id", Integer, primary_key=True)  # Menu ID (part of the composite primary key)
