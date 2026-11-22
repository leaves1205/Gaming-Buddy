"""
Request models for sign-in, registration and password reset

Sign-in accepts existing short passwords. Registration and new passwords require at least six characters.
"""
from typing import Optional  # Standard-library optional type annotations

from pydantic import BaseModel, ConfigDict, Field  # Request model base, configuration and field constraints


class LoginBody(BaseModel):
    """Sign-in request body"""
    model_config = ConfigDict(extra="ignore")  # Ignore extra request fields

    userName: Optional[str] = Field(None, max_length=50)  # Username
    password: Optional[str] = Field(None, max_length=100)  # Password. Existing passwords have no minimum length at sign-in.


class RegisterBody(BaseModel):
    """Registration request body"""
    model_config = ConfigDict(extra="ignore")  # Ignore extra request fields

    userName: Optional[str] = Field(None, max_length=50)  # Username
    password: Optional[str] = Field(None, min_length=6, max_length=100)  # Password (at least six characters)


class SubmitPwdBody(BaseModel):
    """Password reset request body"""
    model_config = ConfigDict(extra="ignore")  # Ignore extra request fields

    oldPassword: Optional[str] = Field(None, max_length=100)  # Current password
    newPassword: Optional[str] = Field(None, min_length=6, max_length=100)  # New password (at least six characters)
