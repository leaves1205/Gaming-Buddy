import request from '@/utils/request'

//Edit profile
export function updateProfile(data) {
  return request({
    url: '/system/user/profile',
    method: 'put',
    data: data
  })
}

//Reset password
export function updatePwd(data) {
  return request({
    url: '/system/user/profile/updatePwd',
    method: 'put',
    data: data
  })
}

//Use params: query to pass filters in the URL.
//1. GET requests normally have no body.
//2. A request body binding cannot read filters from a GET request with no body.
//3. params is serialized into the URL query string.

//List users
export function selectUserList(query) {
  return request({
    url: '/system/user/selectUserList',
    method: 'get',
    params: query
  })
}

//Get user details by ID
export function selectUserByUserId(userId) {
  return request({
    url: '/system/user/selectUserByUserId/' + userId,
    method: 'get'
  })
}

//Add a user
export function insertUser(data) {
  return request({
    url: '/system/user/insertUser',
    method: 'post',
    data: data
  })
}

//Edit a user
export function updateUser(data) {
  return request({
    url: '/system/user/updateUser',
    method: 'put',
    data: data
  })
}

//Delete User
export function deleteUserByUserIds(userIds) {
  return request({
    url: '/system/user/deleteUserByUserIds/' + userIds,
    method: 'delete'
  })
}
