import request from '@/utils/request'

//List all roles
export function selectAllRole() {
  return request({
    url: '/system/role/selectAllRole',
    method: 'get'
  })
}

//List roles
export function selectRoleList(query) {
  return request({
    url: '/system/role/selectRoleList',
    method: 'get',
    params: query
  })
}

//Get role details by ID
export function selectRoleByRoleId(roleId) {
  return request({
    url: '/system/role/selectRoleByRoleId/' + roleId,
    method: 'get'
  })
}

//Add Role
export function insertRole(data) {
  return request({
    url: '/system/role/insertRole',
    method: 'post',
    data: data
  })
}

//Edit Role
export function updateRole(data) {
  return request({
    url: '/system/role/updateRole',
    method: 'put',
    data: data
  })
}

//Delete Role
export function deleteRoleByRoleIds(roleIds) {
  return request({
    url: '/system/role/deleteRoleByRoleIds/' + roleIds,
    method: 'delete'
  })
}
