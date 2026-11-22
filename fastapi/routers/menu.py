"""Menu management under /system/menu"""
# FastAPI routes and query parameters
from fastapi import APIRouter, Query

from core.deps import DbDep, LoginUserDep  # Shared authentication and request-scoped session dependencies
from core.response import ajax_error, ajax_success, ajax_success_data, to_ajax  # Shared response builders
from schemas.body import MenuBody  # Menu request body
from services import menu_service  # Menu service

router = APIRouter(prefix="/system/menu", tags=["menu"])  # Module router


@router.get("/selectMenuList")
def select_menu_list(login_user: LoginUserDep, db: DbDep,
                     menuName: str | None = Query(None)):  # Optional partial menu name filter
    """List all menus for admins and role-filtered menus for other users"""
    menus = menu_service.select_menu_list(db, login_user.userId, menuName)  # The service layer filters by role
    return ajax_success_data(menus)  # Return a flat list. The frontend builds the tree.


@router.post("/insertMenu")
def insert_menu(body: MenuBody, login_user: LoginUserDep, db: DbDep):
    """Add a menu"""
    return to_ajax(menu_service.insert_menu(db, body))  # Build the response from the affected row count


@router.get("/selectMenuByMenuId/{menuId}")
def select_menu_by_menu_id(menuId: int, login_user: LoginUserDep, db: DbDep):
    """Get menu details by ID"""
    menu = menu_service.get_menu_by_id(db, menuId)  # Look up by primary key
    return ajax_success_data(menu) if menu is not None else ajax_success()  # Omit data if no record was found


@router.put("/updateMenu")
def update_menu(body: MenuBody, login_user: LoginUserDep, db: DbDep):
    """Edit a menu"""
    # A menu cannot be its own parent
    if body.menuId is not None and body.menuId == body.parentId:  # The menu ID matches the parent ID
        return ajax_error("A menu cannot be its own parent")
    return to_ajax(menu_service.update_menu_by_id(db, body))  # Update non-null fields only


@router.delete("/deleteMenuByMenuId/{menuId}")
def delete_menu_by_menu_id(menuId: int, login_user: LoginUserDep, db: DbDep):
    """Delete a menu"""
    if menu_service.count_child_menus(db, menuId) > 0:  # Prevent deletion of menus with children
        return ajax_error("Delete the child menus before deleting this menu")
    return to_ajax(menu_service.delete_menu_by_id(db, menuId))  # Clean up associated role_menu records


@router.get("/selectRoleMenuTree/{roleId}")
def select_role_menu_tree(roleId: int, login_user: LoginUserDep, db: DbDep):
    """Return the menu picker tree and the IDs already assigned to the role"""
    menus = menu_service.select_menu_list(db, login_user.userId, None)  # Menus visible to the current user
    checked_keys = menu_service.select_menu_ids_by_role_id(db, roleId)  # Menu IDs assigned to the role
    trees = menu_service.build_menu_tree_select(menus)  # Build the picker tree
    return ajax_success(checkedKeys=checked_keys, menus=trees)  # Selected keys and tree structure


@router.get("/selectRoleMenusTree")
def select_role_menus_tree(login_user: LoginUserDep, db: DbDep):
    """Get a menu picker tree for the current user"""
    menus = menu_service.select_menu_list(db, login_user.userId, None)  # Visible menus
    return ajax_success_data(menu_service.build_menu_tree_select(menus))  # Picker tree structure


@router.get("/getRouters")
def get_routers(login_user: LoginUserDep, db: DbDep):
    """Build the current user's dynamic frontend routes"""
    routers = menu_service.get_routers(db, login_user.userId)  # Build the route tree in the service layer
    return ajax_success_data(routers)  # Used by router.addRoute on the frontend
