"""Profile under /system/user/profile"""
# Standard-library file and directory operations for removing old avatars
import os

# FastAPI routes, file uploads and request headers
from fastapi import APIRouter, File, Header, UploadFile

from core.config import settings  # Upload base path
from core.deps import DbDep, LoginUserDep  # Shared authentication and request-scoped session dependencies
from core.files import save_upload  # Shared chunked file storage
from core.response import ajax_error, ajax_success, to_ajax  # Shared response builders
from core.security import extract_token, invalidate_token, parse_token  # Token extraction, revocation and parsing
from schemas.auth import SubmitPwdBody  # Password reset request body
from schemas.body import UserBody  # User request body
from services import user_service  # User service

router = APIRouter(prefix="/system/user/profile", tags=["profile"])  # Module router


def _remove_old_avatar(old_url: str | None) -> None:
    """Remove the old avatar file from the avatar directory and ignore cleanup errors"""
    if not old_url or not old_url.startswith("/profile/avatar/"):
        return  # Skip empty URLs and avatars that are not local uploads
    file_path = os.path.join(settings.profile, "avatar", os.path.basename(old_url))  # Build the local file path
    try:
        os.remove(file_path)
    except OSError:
        pass  # Ignore missing or locked files so cleanup cannot interrupt the avatar update


@router.post("/avatar")
async def avatar(login_user: LoginUserDep, db: DbDep,
                 file: UploadFile = File(...)):
    """Save the avatar under {profile}/avatar, return its URL and clean up the old file"""
    try:
        saved = await save_upload(file, "avatar")  # Save the file in chunks using a hyphenless UUID and its extension
        old_url = user_service.get_user_avatar(db, login_user.userId)  # Previous avatar URL
        if user_service.update_user_avatar(db, login_user.userId, saved["url"]) > 0:  # Update the avatar in the database
            _remove_old_avatar(old_url)  # Remove the previous file. Cleanup errors do not affect the result.
            return ajax_success(imgUrl=saved["url"])  # Return the new avatar URL
    except ValueError:  # Handle the empty-file error from save_upload with the standard failure message
        pass
    return ajax_error("Avatar upload failed. Please try again.")  # Empty file or failed update


@router.put("")
def update_profile(body: UserBody, login_user: LoginUserDep, db: DbDep):
    """Use the requested username and gender. Update the avatar only when supplied."""
    if login_user.userId is None:  # Fail immediately if the user ID is missing
        return to_ajax(0)

    if body.userName is not None and user_service.user_name_taken(db, body.userName, login_user.userId):
        return ajax_error("This username is already taken")  # Check for duplicate usernames among other accounts

    fields: dict = {}  # Collect only non-null columns to update
    if body.userName is not None:  # Use the requested username
        fields["user_name"] = body.userName
    if body.sex is not None:  # Use the requested gender
        fields["sex"] = body.sex
    if body.avatar:  # Update the avatar only when a nonempty value is supplied
        fields["avatar"] = body.avatar
    return to_ajax(user_service.update_user_by_id(db, login_user.userId, fields))  # Update supplied fields dynamically


@router.put("/updatePwd")
def update_pwd(body: SubmitPwdBody, login_user: LoginUserDep, db: DbDep,
               authorization: str | None = Header(default=None)):  # Read the request token so it can be revoked after the password changes
    current = user_service.get_user_password(db, login_user.userId)  # Fetch the current password from the database because token snapshots can be stale
    if current is None:  # User not found
        return ajax_error("Password change failed. Review the form and try again.")

    if body.newPassword == current:  # The old and new passwords match
        return ajax_error("The new password must differ from the current password")
    if body.oldPassword != current:  # The current password is incorrect
        return ajax_error("Incorrect current password")

    if user_service.reset_user_pwd(db, login_user.userId, body.newPassword) > 0:  # Update succeeded
        token = extract_token(authorization)  # Extract the current token
        if token:  # Revoke the current token and require a new sign-in after the password change
            claims = parse_token(token)  # Decode the claims to get the expiry
            if claims and "exp" in claims:
                invalidate_token(token, claims["exp"] * 1000)  # Revoke the token until it expires. Convert seconds to milliseconds.
        return ajax_success()
    return ajax_error("Password change failed. Review the form and try again.")  # Update failed
