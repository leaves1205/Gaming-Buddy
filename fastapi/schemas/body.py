"""
Request models for users, roles and menus

All fields are optional. Updates use only fields explicitly supplied with non-null values.
max_length, ge and le mirror database constraints and reject invalid request values.
"""
from typing import Optional  # Standard-library optional type annotations

from pydantic import BaseModel, ConfigDict, Field  # Request model base, configuration and field constraints


class UserBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore extra request fields

    userId: Optional[int] = None  # User ID identifying the record to update
    userName: Optional[str] = Field(None, max_length=50)  # Username limited by the database column width
    sex: Optional[int] = Field(None, ge=0, le=1)  # Gender (0 male, 1 female)
    avatar: Optional[str] = Field(None, max_length=255)  # Avatar URL
    password: Optional[str] = Field(None, max_length=100)  # Password
    roleId: Optional[int] = None  # Role ID
    createTime: Optional[str] = None  # Creation time as a 'yyyy-MM-dd HH:mm:ss' string


class RoleBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore extra request fields

    roleId: Optional[int] = None  # Role ID identifying the record to update
    roleName: Optional[str] = Field(None, max_length=255)  # Role name limited by the database column width
    roleSort: Optional[int] = None  # Display order
    remark: Optional[str] = Field(None, max_length=500)  # Notes limited by the database column width
    createTime: Optional[str] = None  # Creation time as a 'yyyy-MM-dd HH:mm:ss' string
    menuIds: Optional[list[int]] = None  # Permitted menu IDs for role_menu associations


class MenuBody(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore extra request fields

    menuId: Optional[int] = None  # Menu ID identifying the record to update
    menuName: Optional[str] = Field(None, max_length=100)  # Menu name limited by the database column width
    parentId: Optional[int] = None  # Parent menu ID (0 for top level)
    menuSort: Optional[int] = None  # Display order
    path: Optional[str] = Field(None, max_length=255)  # Route path limited by the database column width
    component: Optional[str] = Field(None, max_length=255)  # Component path limited by the database column width
    menuType: Optional[str] = Field(None, max_length=10)  # Menu type (M for directory, C for menu item)
    icon: Optional[str] = Field(None, max_length=100)  # Icon name limited by the database column width
    createTime: Optional[str] = None  # Creation time as a 'yyyy-MM-dd HH:mm:ss' string
