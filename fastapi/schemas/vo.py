"""
View models for the authenticated user and user snapshot

Use camelCase fields to match the frontend JSON keys.
createTime is a 'yyyy-MM-dd HH:mm:ss' string.
"""
from typing import Optional  # Standard-library optional type annotations

from pydantic import BaseModel, ConfigDict  # Model base and configuration


class UserSnapshot(BaseModel):
    """Store the user snapshot in the token's user_key claim"""
    model_config = ConfigDict(extra="ignore")  # Ignore extra fields for compatibility with older tokens

    userId: Optional[int] = None  # User ID
    userName: Optional[str] = None  # Username
    sex: Optional[int] = None  # Gender
    avatar: Optional[str] = None  # Avatar URL
    createTime: Optional[str] = None  # Creation time as a 'yyyy-MM-dd HH:mm:ss' string
    roleId: Optional[int] = None  # Role ID
    roleName: Optional[str] = None  # Role name


class LoginUser(BaseModel):
    """Authenticated user identity with extra claims ignored"""
    model_config = ConfigDict(extra="ignore")  # Ignore extra claims for compatibility with older tokens

    userId: Optional[int] = None  # User ID
    loginTime: Optional[int] = None  # Sign-in timestamp in milliseconds, set when issuing the token
    expireTime: Optional[int] = None  # Expiry timestamp in milliseconds, set when issuing the token
    user: Optional[UserSnapshot] = None  # User snapshot
