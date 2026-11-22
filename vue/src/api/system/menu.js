import request from '@/utils/request'

//List menus
export function selectMenuList(query) {
  return request({
    url: '/system/menu/selectMenuList',
    method: 'get',
    params: query
  })
}

//Add a menu
export function insertMenu(data) {
  return request({
    url: '/system/menu/insertMenu',
    method: 'post',
    data: data
  })
}

//Get menu details by ID
export function selectMenuByMenuId(menuId) {
  return request({
    url: '/system/menu/selectMenuByMenuId/' + menuId,
    method: 'get'
  })
}

//Edit a menu
export function updateMenu(data) {
  return request({
    url: '/system/menu/updateMenu',
    method: 'put',
    data: data
  })
}

//Delete a menu
export function deleteMenuByMenuId(menuId) {
  return request({
    url: '/system/menu/deleteMenuByMenuId/' + menuId,
    method: 'delete'
  })
}

//Get the menu tree for a role
export function selectRoleMenuTree(roleId) {
  return request({
    url: '/system/menu/selectRoleMenuTree/' + roleId,
    method: 'get'
  })
}

//Get the menu picker tree for the frontend
export function selectRoleMenusTree() {
  return request({
    url: '/system/menu/selectRoleMenusTree',
    method: 'get'
  })
}

//Get the current user's menu permissions
export function getRouters() {
  return request({
    url: '/system/menu/getRouters',
    method: 'get'
  })
}
