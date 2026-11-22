"""
Sign-in, registration, sign-out and user details
"""
# FastAPI routes, headers and raw responses
from fastapi import APIRouter, Header, Response

from core.common import fmt_dt  # Date formatting
from core.deps import DbDep, LoginUserDep  # Shared authentication and request-scoped session dependencies
from core.response import ajax_error, ajax_success, ajax_success_data  # Shared response builders
from core.security import create_token, extract_token, invalidate_token, parse_token  # Token utilities
from schemas.auth import LoginBody, RegisterBody  # Sign-in and registration request bodies
from schemas.vo import LoginUser, UserSnapshot  # Authenticated user and snapshot models
from services import user_service  # User service

router = APIRouter(tags=["auth"])  # Module router with no prefix


def _make_snapshot(user) -> UserSnapshot:
    """Convert a User to a token snapshot without the password or other sensitive data"""
    return UserSnapshot(  # Copy each field using camelCase keys
        userId=user.user_id,  # User ID
        userName=user.user_name,  # Username
        sex=user.sex,  # Gender
        avatar=user.avatar,  # Avatar URL
        createTime=fmt_dt(user.create_time),  # Creation time as a formatted string
        roleId=user.role_id,  # Role ID
        roleName=None,  # Omit the role name from the token
    )


@router.post("/login")
def login(body: LoginBody, db: DbDep):
    """Validate the username and password, then return a token on success"""
    # 1. Validate the input. Missing input returns HTTP 200 with code 500.
    if (not body.userName or not body.password  # Treat empty or whitespace-only values as missing
            or not body.userName.strip() or not body.password.strip()):
        return ajax_error("Username or password is missing")

    # 2. Check that the user exists
    user = user_service.get_user_by_name(db, body.userName)  # Look up the user by username
    if user is None:
        return ajax_error("Invalid username")  # Keep the response generic to limit account enumeration

    # 3. Check the password using a plain-text comparison
    if body.password != user.password:
        return ajax_error("Incorrect password")

    # 4. Issue a JWT
    token = create_token(LoginUser(userId=user.user_id, user=_make_snapshot(user)))  # Store the user snapshot in the token

    # 5. Return the token
    return ajax_success(token=token)  # {code:200, msg, token}


@router.post("/register")
def register(body: RegisterBody, db: DbDep):
    """Validate the username and password and save the new account"""
    if not body.userName:
        return ajax_error("Username is required")  # HTTP 200 + code 500
    if not body.password:
        return ajax_error("Password is required")

    if not user_service.register_user(db, body.userName, body.password):  # False indicates the username is already taken
        return ajax_error("This username is taken. Choose another username to register.")
    return ajax_success()


@router.post("/logout")
def logout(authorization: str | None = Header(default=None)):
    """Revoke the token on sign-out and always return HTTP 200 with an empty body"""
    token = extract_token(authorization)  # Extract the raw token, if present
    if token:
        claims = parse_token(token)  # Decode the claims to get the expiry
        if claims and "exp" in claims:  # Proceed if decoding succeeds and exp is present
            invalidate_token(token, claims["exp"] * 1000)  # Revoke the token until it expires. Convert seconds to milliseconds.
    return Response(status_code=200)  # Return HTTP 200 with an empty body


@router.get("/getInfo")
def get_info(login_user: LoginUserDep, db: DbDep):
    """Get the current user and role name"""
    user = user_service.get_user_by_id(db, login_user.userId)  # Fetch the latest details from the database
    return ajax_success_data(user)  # Omit data when it is None
