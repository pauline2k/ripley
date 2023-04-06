import utils from './api-utils'

export function becomeUser(canvasSiteId: number, uid: string) {
  return utils.post('/api/auth/become_user', {canvasSiteId, uid}, true)
}

export function devAuthLogIn(canvasSiteId: number, uid: string, password: string) {
  return utils.post('/api/auth/dev_auth', {canvasSiteId, password, uid}, true)
}

export function getCasLoginURL() {
  return utils.get('/api/auth/cas_login_url', true)
}

export function getCasLogoutUrl() {
  return utils.get('/api/auth/logout', true)
}

export function logOut() {
  return utils.get('/api/auth/logout', true)
}

export function updateUserSession(canvasSiteId: number, redirectOnError?: boolean) {
  return utils.post('/api/auth/update_user_session', {canvasSiteId}, redirectOnError)
}
