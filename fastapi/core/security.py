"""
Token handling

- Sign JWTs with HS512
- Store user data as a JSON string in the custom user_key claim
- Add signed-out tokens to the in-memory revocation list and remove expired entries during validation

The in-memory revocation list is intended for a single process such as the default uvicorn worker or its reload child.
Revocation is process-local and is lost on restart. Signed-out tokens can remain valid until expiry across workers or restarts.
"""
import time  # Standard-library millisecond timestamps

import jwt  # PyJWT encoding and decoding

from core.config import settings  # Read the signing key and token lifetime
from schemas.vo import LoginUser  # Authenticated user snapshot model

# Revocation list mapping tokens to expiration timestamps in milliseconds
_blacklisted_tokens: dict[str, int] = {}


def extract_token(authorization: str | None) -> str | None:
    """Extract the token from Authorization and strip the Bearer prefix"""
    if not authorization:  # Request header is missing
        return None
    if authorization.startswith("Bearer "):  # Standard format: Bearer {token}
        return authorization[7:]  # Strip the seven-character "Bearer " prefix
    return authorization  # Accept the header value as-is when there is no prefix


def create_token(login_user: LoginUser) -> str:
    """Issue a JWT for the user"""
    now_ms = int(time.time() * 1000)  # Current timestamp in milliseconds
    expire_ms = now_ms + settings.token_expire_minutes * 60 * 1000  # Expiry timestamp in milliseconds equals the current time plus the configured lifetime

    login_user.loginTime = now_ms  # Save the sign-in time in the token snapshot
    login_user.expireTime = expire_ms  # Save the expiry time for later validation

    claims = {"user_key": login_user.model_dump_json(), "exp": expire_ms // 1000}  # Store the user snapshot as JSON and use seconds for the standard exp claim
    return jwt.encode(claims, settings.token_secret, algorithm="HS512")  # Sign with HS512 and return the token string


def parse_token(token: str) -> dict | None:
    """Return decoded token claims, or None if decoding fails or the token has expired"""
    try:
        return jwt.decode(token, settings.token_secret, algorithms=["HS512"])  # Return claims after verifying the signature and exp
    except Exception:
        return None  # Reject incorrect signatures, expired tokens and malformed tokens


def parse_login_user(token: str) -> LoginUser | None:
    """Read the authenticated user from the token, or return None on failure"""
    claims = parse_token(token)  # Decode the claims first
    if not claims or "user_key" not in claims:  # Decoding failed or the user claim is missing
        return None
    try:
        # extra="ignore" skips additional claim fields
        return LoginUser.model_validate_json(claims["user_key"])  # Deserialize the JSON string into a LoginUser model
    except Exception:
        return None  # Model validation failed, such as when a field has the wrong type


def invalidate_token(token: str | None, expire_ms: int) -> None:
    """Add a token to the revocation list at sign-out"""
    if not token:  # Skip revocation when no token is present
        return
    _blacklisted_tokens[token] = expire_ms  # Keep the expiry timestamp for removal during a later check


def is_token_blacklisted(token: str | None) -> bool:
    """Check whether the token is revoked and remove expired entries during the check"""
    if not token:  # Leave missing tokens to the remaining validation steps
        return False
    expire_ms = _blacklisted_tokens.get(token)  # Look up the token in the revocation list
    if expire_ms is None:
        return False  # The token is absent from the revocation list
    if expire_ms < time.time() * 1000:  # The recorded expiry has passed and the token has expired naturally
        _blacklisted_tokens.pop(token, None)  # Remove the expired entry during this check
        return False
    return True  # Treat listed, unexpired tokens as invalid because the user signed out
