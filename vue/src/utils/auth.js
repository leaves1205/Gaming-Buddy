/**
 * Get the current authentication token
 */
export function getToken() {
  return localStorage.getItem('tokenKey')
}

/**
 * Save the authentication token
 */
export function setToken(token) {
  return localStorage.setItem('tokenKey', token)
}

/**
 * Remove the authentication token
 */
export function removeToken() {
  return localStorage.removeItem('tokenKey')
}
