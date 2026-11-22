"""
Authentication dependencies

Declare login_user: LoginUser = Depends(get_current_login_user) on authenticated routes
Extract the token, parse the user, check revocation and check expiry. Any failure returns HTTP 401.

Common route dependency aliases appear at the end of this module (DbDep, LoginUserDep and PageDep).
Reuse the Annotated aliases in route signatures to avoid repeating Depends(...).
"""
import time  # Standard-library timestamps for expiry checks
from typing import Annotated  # Standard-library type annotations for dependency aliases

from fastapi import Depends, Header, Query  # FastAPI dependency injection, request headers and query parameters
from sqlalchemy.orm import Session  # Session type annotation

from core.database import get_db  # Per-request session dependency
from core.exceptions import AuthError  # Authentication failure exception
from core.security import extract_token, is_token_blacklisted, parse_login_user  # Token extraction, revocation and parsing utilities
from schemas.vo import LoginUser  # Authenticated user snapshot model


def get_current_login_user(authorization: str | None = Header(default=None)) -> LoginUser:
    # 1. Extract the token
    token = extract_token(authorization)  # Strip the Bearer prefix
    if not token:
        raise AuthError()  # A missing header or token means the user is unauthenticated

    # 2. Parse the user details
    login_user = parse_login_user(token)  # Parse the user snapshot in the JWT
    if login_user is None:
        raise AuthError()  # Invalid signature, expired token or invalid format

    # 3. Check the revocation list. Signing out revokes the token.
    if is_token_blacklisted(token):
        raise AuthError()  # Reject tokens used after sign-out

    # 4. Check expiry
    if login_user.expireTime is None or login_user.expireTime - time.time() * 1000 <= 0:
        raise AuthError()  # The expiry is missing or is earlier than the current millisecond timestamp

    return login_user  # Return the authenticated user once all checks pass


def get_current_token(authorization: str | None = Header(default=None)) -> str | None:
    """Extract the raw token for routes that can run without authentication, such as sign-out"""
    return extract_token(authorization)  # Return None when the token is missing


# ==================== Common route dependency aliases ====================

DbDep = Annotated[Session, Depends(get_db)]  # Request-scoped database session, declared as db: DbDep
LoginUserDep = Annotated[LoginUser, Depends(get_current_login_user)]  # Authentication, declared as login_user: LoginUserDep


class PageParams:
    """Pagination query dependency, declared as page: PageDep

    Read the required pageNum and pageSize query parameters and enforce their bounds.
    Require pageNum >= 1 and 1 <= pageSize <= 500. The validation handler returns English messages.
    The helper in core.common.paginate also enforces these bounds.
    """

    def __init__(
        self,
        pageNum: int = Query(..., ge=1),  # Page number (required, minimum 1)
        pageSize: int = Query(..., ge=1, le=500),  # Items per page (required, 1 to 500)
    ):
        self.pageNum = pageNum  # Expose page.pageNum to routes and services
        self.pageSize = pageSize  # Expose page.pageSize to routes and services


PageDep = Annotated[PageParams, Depends()]  # Pagination parameters, declared as page: PageDep
