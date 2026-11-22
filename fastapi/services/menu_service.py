"""
Menu service and dynamic route construction

Menu dictionaries use camelCase keys. children is always a list.
Frontend route rules
- Top-level directory (M) prefixes path with '/'. Set alwaysShow=true when it has children.
- Top-level item (C) uses path='/', omits its own meta and wraps one child route whose meta includes path.
- A nested directory (M) without a component uses ParentView. Other unspecified components default to Layout.
- Omit empty fields
"""
# SQLAlchemy query and count expressions
from sqlalchemy import func, select
from sqlalchemy.orm import Session  # Session type annotation

from core.common import (  # Shared utilities
    body_fields, delete_by_pks, insert_row, like_if, row_to_dict, update_by_pk, where_if,
)
from models.entities import Menu, RoleMenu, User  # ORM entities for menus, associations and users
from schemas.body import MenuBody  # Menu request model

# Super administrator role ID
ADMIN_ROLE_ID = 1  # Skip permission filters for this role because it can access all menus

_MENU_COLS = (  # Selected menu columns mapped to keys by row_to_dict
    Menu.menu_id, Menu.menu_name, Menu.parent_id, Menu.menu_sort,
    Menu.path, Menu.component, Menu.menu_type, Menu.icon, Menu.create_time,
)


def menu_row_to_dict(row) -> dict:
    """Convert database rows to camelCase menu dictionaries"""
    return row_to_dict(row, {"children": [], "userId": None})  # Tree construction populates children. userId is a placeholder.


def _get_role_id_by_user(db: Session, user_id: int) -> int | None:
    """Look up the user's role ID"""
    return db.scalar(select(User.role_id).where(User.user_id == user_id))  # Query one value and return None when no row is found


def _query_menus(db: Session, role_id: int | None, menu_name: str | None) -> list[dict]:
    """Return all menus when role_id is None or assigned menus for the role. menuName is a partial filter."""
    stmt = select(*_MENU_COLS).select_from(Menu)  # Explicitly select the main table
    if role_id is not None:  # Join role_menu to filter accessible menus for regular users
        stmt = stmt.join(RoleMenu, Menu.menu_id == RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
    stmt = where_if(stmt, like_if(Menu.menu_name, menu_name))  # Add filters for populated values
    stmt = stmt.order_by(Menu.parent_id, Menu.menu_sort)  # Sort by parent and then display order to prepare for tree construction
    return [menu_row_to_dict(r) for r in db.execute(stmt).all()]  # Return a list of camelCase dictionaries


def select_menu_list(db: Session, current_user_id: int, menu_name: str | None = None) -> list[dict]:
    """List all menus for administrators and filter by role for other users"""
    role_id = _get_role_id_by_user(db, current_user_id)  # Look up the current user's role
    if role_id == ADMIN_ROLE_ID:  # Administrators can view all menus
        return _query_menus(db, None, menu_name)
    return _query_menus(db, role_id, menu_name)  # Other users see menus assigned to their role


def select_menu_ids_by_role_id(db: Session, role_id: int) -> list[int]:
    """Get permitted menu IDs by role ID"""
    stmt = (  # Look up assigned menu IDs in role_menu
        select(Menu.menu_id)
        .join(RoleMenu, Menu.menu_id == RoleMenu.menu_id, isouter=True)
        .where(RoleMenu.role_id == role_id)
        .order_by(Menu.parent_id, Menu.menu_sort)
    )
    return [r[0] for r in db.execute(stmt).all()]  # Read the first column (menu_id)


# ==================== Menu picker tree ====================

def build_menu_tree(menus: list[dict]) -> list[dict]:
    """Build a tree from flat menus. Deduplicate by menuId and treat missing parents as roots."""
    unique: list[dict] = []  # Deduplicated menus
    seen: set[int] = set()  # Previously seen menu IDs
    for m in menus:  # Deduplicate by menuId after the join
        if m["menuId"] not in seen:
            seen.add(m["menuId"])
            unique.append(m)
    id_map = {m["menuId"]: m for m in unique}  # Map menu IDs to dictionaries for parent lookup
    roots: list[dict] = []  # Top-level menus
    for m in unique:  # Link entries to their parents
        m["children"] = []  # Reset children to prevent duplicate attachments
        if m["parentId"] == 0 or m["parentId"] is None:  # A zero or empty parentId identifies a root
            roots.append(m)
        else:
            parent = id_map.get(m["parentId"])  # Find the parent menu
            if parent is not None:
                parent["children"].append(m)  # Append to the parent's children
            else:
                roots.append(m)  # Treat a menu whose parent is missing as a root
    return roots


def _menu_to_tree_select(node: dict) -> dict:
    """Picker node with id, label and optional children"""
    d = {"id": node["menuId"], "label": node["menuName"]}  # Node structure used by the tree component
    if node["children"]:  # Recursively include children if present
        d["children"] = [_menu_to_tree_select(c) for c in node["children"]]
    return d


def build_menu_tree_select(menus: list[dict]) -> list[dict]:
    """Build the frontend picker tree"""
    return [_menu_to_tree_select(t) for t in build_menu_tree(menus)]  # Build the tree and convert each root


# ==================== Dynamic routes ====================

def get_routers(db: Session, user_id: int) -> list[dict]:
    """Get the user's menu tree and format it as frontend routes"""
    role_id = _get_role_id_by_user(db, user_id)  # Look up the user's role
    if role_id == ADMIN_ROLE_ID:  # Administrators see every menu
        menus = _query_menus(db, None, None)
    else:  # Other users see menus assigned to their role
        menus = _query_menus(db, role_id, None)

    # Fetch missing parents so child-only permissions still produce routes
    own_ids = {m["menuId"] for m in menus}  # Set of menu IDs already returned
    missing_parent_ids = {  # Missing parent IDs, excluding top-level entries
        m["parentId"] for m in menus
        if m["parentId"] not in (None, 0) and m["parentId"] not in own_ids
    }
    if missing_parent_ids:  # Fetch any missing parents
        rows = db.execute(select(*_MENU_COLS).where(Menu.menu_id.in_(missing_parent_ids))).all()
        menus.extend(menu_row_to_dict(r) for r in rows)  # Append to the menu list

    # Initialize all child lists before linking to avoid dropping children
    menu_map = {m["menuId"]: m for m in menus}  # Map menu IDs to menu dictionaries
    for m in menus:
        m["children"] = []  # Initialize all child lists first
    roots: list[dict] = []  # Top-level menus
    for m in menus:  # Then link the entries
        if m["parentId"] == 0:  # Top-level menu
            roots.append(m)
        else:
            parent = menu_map.get(m["parentId"])  # Find the parent
            if parent is not None:
                parent["children"].append(m)  # Append to the parent's children

    return _build_routers(roots)  # Format the tree as frontend routes


def _build_routers(menus: list[dict]) -> list[dict]:
    """Convert menu trees to frontend routes"""
    routers: list[dict] = []  # Frontend route results
    for m in menus:  # Convert each menu
        parent_is_root = m["parentId"] == 0  # Top-level menu or directory when the parent ID is zero
        menu_type = m["menuType"]  # Menu type (M for directory, C for menu item)
        component = m["component"]  # Optional configured component path

        # Add the menu ID to top-level route names for uniqueness
        router_name = m["path"]  # Default to the path for the route name
        if parent_is_root and m["menuId"] is not None:  # Top-level entry with a menu ID
            router_name = f"{m['path']}_{m['menuId']}"  # Append a suffix to keep the name unique

        # Prefix top-level directories with '/'. Home uses '/' and other top-level menus use their configured path prefixed with '/'.
        router_path = m["path"]  # Use the configured value by default
        if parent_is_root and menu_type == "M":  # Prefix top-level directories with '/'
            router_path = "/" + m["path"]
        elif parent_is_root and menu_type == "C":  # Top-level menu item
            # Keep Home (index) under '/' for the root redirect in permission.js.
            # Give other top-level menus distinct paths so their active states do not overlap.
            router_path = "/" if m["path"] == "index" else "/" + (m["path"] or "")

        # Use the configured component for entries other than top-level items. Unconfigured nested directories use ParentView. Remaining entries use Layout.
        router_component = "Layout"  # Default layout
        if component and not (parent_is_root and menu_type == "C"):  # Configured component on an entry other than a top-level menu item
            router_component = component  # Use the specified page component
        elif not component and (not parent_is_root and menu_type == "M"):  # Nested directory with no component
            router_component = "ParentView"  # Parent view wrapper

        router: dict = {  # Single route node
            "name": router_name,  # Unique route name
            "path": router_path,  # Route path
            "component": router_component,  # Component (layout, page or ParentView)
            "meta": {"title": m["menuName"], "icon": m["icon"]},  # Title and icon
        }

        children = m["children"]  # Child menus
        if children and menu_type == "M":  # Directory with children
            # Display the directory and recursively process its children
            router["alwaysShow"] = True  # Always show the directory, even with one child
            router["children"] = _build_routers(children)  # Convert child menus recursively
        elif parent_is_root and menu_type == "C":  # Special handling for top-level items
            # Put the page and metadata on the sole child route
            router.pop("meta")  # Remove metadata from the parent
            child: dict = {"name": m["path"]}  # Build the single child route
            if m["path"] is not None:  # Include the path if populated
                # Home uses child path 'index' under '/'. Other top-level items mount an empty path under '/xxx'.
                child["path"] = "index" if m["path"] == "index" else ""
            if component is not None:  # Include the component if set
                child["component"] = component
            child["meta"] = {"title": m["menuName"], "icon": m["icon"], "path": m["path"]}  # Put metadata on the child route
            router["children"] = [child]  # Assign the sole child

        routers.append(router)  # Append to the results
    return routers


# ==================== Menu CRUD ====================

def get_menu_by_id(db: Session, menu_id: int) -> dict | None:
    """Get menu by primary key"""
    row = db.execute(select(*_MENU_COLS).where(Menu.menu_id == menu_id)).first()  # Fetch the first matching row
    return menu_row_to_dict(row) if row else None  # Return None if no record exists


def insert_menu(db: Session, body: MenuBody) -> int:
    """Add a menu"""
    return insert_row(db, Menu, body_fields(body, skip=("menuId",)))  # Insert and commit with the shared single-table helper


def update_menu_by_id(db: Session, body: MenuBody) -> int:
    """Update non-null fields by menu ID"""
    if body.menuId is None:  # The primary key is required to find the record
        return 0
    return update_by_pk(db, Menu, Menu.menu_id, body.menuId, body_fields(body, skip=("menuId",)))  # Use the shared dynamic update helper


def delete_menu_by_id(db: Session, menu_id: int) -> int:
    """Delete a menu. ON DELETE CASCADE removes its role_menu entries."""
    return delete_by_pks(db, Menu, Menu.menu_id, [menu_id])  # Use the shared primary-key deletion helper


def count_child_menus(db: Session, menu_id: int) -> int:
    """Count immediate children before deletion to prevent orphaned entries"""
    return db.scalar(select(func.count()).select_from(Menu).where(Menu.parent_id == menu_id)) or 0