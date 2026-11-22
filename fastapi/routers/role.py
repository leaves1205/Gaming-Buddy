"""Role management under /system/role"""
# FastAPI routes and query parameters
from fastapi import APIRouter, Query

from core.common import split_ids  # Parse comma-separated IDs for deletion
from core.deps import DbDep, LoginUserDep, PageDep  # Shared pagination, authentication and request-scoped session dependencies
from core.response import ajax_error, ajax_success, ajax_success_data, page_data, to_ajax  # Shared response builders
from schemas.body import RoleBody  # Role request body
from services import role_service  # Role service

router = APIRouter(prefix="/system/role", tags=["role"])  # Module router

# The built-in administrator and regular user roles are protected from deletion
PROTECTED_ROLE_IDS = {1, 2}  # Set of protected role IDs


@router.get("/selectAllRole")
def select_all_role(login_user: LoginUserDep, db: DbDep):
    """List all roles without pagination for dropdowns"""
    return ajax_success_data(role_service.select_role_list(db))  # Complete role list


@router.get("/selectRoleList")
def select_role_list(page: PageDep, login_user: LoginUserDep, db: DbDep,  # Shared pagination, authentication and session dependencies
                     roleId: int | None = Query(None),  # Optional role ID filter
                     roleName: str | None = Query(None)):  # Optional partial role name filter
    """Get a paginated list of roles"""
    total, rows = role_service.select_role_page(db, page.pageNum, page.pageSize, roleId, roleName)  # Paginate roles in the service layer
    return page_data(rows, total)  # {total, rows, code, msg}


@router.get("/selectRoleByRoleId/{roleId}")
def select_role_by_role_id(roleId: int, login_user: LoginUserDep, db: DbDep):
    """Get role details by ID"""
    role = role_service.get_role_by_id(db, roleId)  # Look up by primary key
    return ajax_success_data(role) if role is not None else ajax_success()  # Omit data if no record was found


@router.post("/insertRole")
def insert_role(body: RoleBody, login_user: LoginUserDep, db: DbDep):
    """Add a role with its menu permissions"""
    return to_ajax(role_service.insert_role(db, body))  # Build the response from the affected row count


@router.put("/updateRole")
def update_role(body: RoleBody, login_user: LoginUserDep, db: DbDep):
    """Edit the role and replace its menu permissions"""
    return to_ajax(role_service.update_role(db, body))  # Build the response from the affected row count


@router.delete("/deleteRoleByRoleIds/{roleIds}")
def delete_role_by_role_ids(roleIds: str, login_user: LoginUserDep, db: DbDep):
    """Delete multiple roles by comma-separated IDs"""
    ids = split_ids(roleIds)  # "1,2,3" -> [1,2,3]
    for role_id in ids:  # Check each role against the protected IDs
        if role_id in PROTECTED_ROLE_IDS:  # The role is protected
            return ajax_error("The built-in administrator and regular user roles cannot be deleted")
    return to_ajax(role_service.delete_role_by_ids(db, ids))  # Delete in bulk
