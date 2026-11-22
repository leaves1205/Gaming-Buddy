"""User management under /system/user. Profile routes are defined separately."""
# FastAPI routes and query parameters
from fastapi import APIRouter, Query

from core.common import body_fields, split_ids  # Convert request bodies to database columns and parse comma-separated deletion IDs
from core.deps import DbDep, LoginUserDep, PageDep  # Shared pagination, authentication and request-scoped session dependencies
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # Shared response builders
from schemas.body import UserBody  # User request body
from services import user_service  # User service

router = APIRouter(prefix="/system/user", tags=["user"])  # Module router with a shared prefix


@router.get("/selectUserList")
def select_user_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # Shared pagination, authentication and session dependencies
                     userId: int | None = Query(None),  # Optional user ID filter
                     userName: str | None = Query(None)):  # Optional partial username filter
    """Get a paginated list of users"""
    total, rows = user_service.page_users(db, page.pageNum, page.pageSize, userId, userName)  # Paginate roles in the service layer
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectUserByUserId/{userId}")
def select_user_by_user_id(userId: int, login_user: LoginUserDep, db: DbDep):
    """Get user details by ID"""
    user = user_service.get_user_by_id(db, userId)  # Look up the user and role name by ID
    # Omit data when it is None
    return ajax_success_data(user) if user is not None else ajax_success()


@router.post("/insertUser")
def insert_user(body: UserBody, login_user: LoginUserDep, db: DbDep):
    """Add a user"""
    return to_ajax(user_service.insert_user(db, body))  # Build the response from the affected row count


@router.put("/updateUser")
def update_user(body: UserBody, login_user: LoginUserDep, db: DbDep):
    """Edit a user"""
    if body.userId is None:  # Fail immediately if the primary key is missing
        return to_ajax(0)
    if body.userName is not None and user_service.user_name_taken(db, body.userName, body.userId):
        return ajax_error("This username is already taken")  # Check for duplicate usernames among other accounts
    return to_ajax(user_service.update_user_by_id(db, body.userId, body_fields(body, skip=("userId",))))  # Update non-null fields only


@router.delete("/deleteUserByUserIds/{userIds}")
def delete_user_by_user_ids(userIds: str, login_user: LoginUserDep, db: DbDep):
    """Delete multiple users by comma-separated IDs"""
    ids = split_ids(userIds)  # "1,2,3" -> [1,2,3]
    if login_user.userId in ids:  # Deleting your own account would leave the current session invalid
        return ajax_error("You cannot delete the currently signed-in user")
    if user_service.count_admins_except(db, ids) == 0:  # Reject deletion if it would remove all admins
        return ajax_error("You cannot delete the last administrator")
    return to_ajax(user_service.delete_user_by_ids(db, ids))  # Delete in bulk
