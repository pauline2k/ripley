import utils from './api-utils'

export function devAuthLogIn(canvasCourseId: number, uid: string, password: string) {
  return utils.post('/api/auth/dev_auth', {canvasCourseId, password, uid}, true)
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

export function updateUserSession(canvasCourseId: number) {
  return utils.post('/api/auth/update_user_session', {canvasCourseId}, true)
}
