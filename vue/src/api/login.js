import request from '@/utils/request'

//Sign in
export function login(data) {
  return request({
    url: '/login', //Backend endpoint
    headers: { //Request headers
      isToken: false //Tell the interceptor to omit the token
    },
    method: 'post', //Use POST as required by the backend
    data: data //Request data
  })
}

//Get the current user's details
export function getInfo() {
  return request({
    url: '/getInfo',
    method: 'get',
  })
}

//Sign out
export function logout() {
  return request({
    url: '/logout',
    method: 'post',
  })
}
