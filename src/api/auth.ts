import axios from 'axios'
import utils from './api-utils'

export function devAuthLogIn(canvasCourseId: number, uid: string, password: string) {
  const url = `${utils.apiBaseUrl()}/api/auth/dev_auth`
  return axios.post(url, {canvasCourseId, password, uid})
}

export function getCasLoginURL() {
  return utils.get('/api/auth/cas_login_url')
}

export function getCasLogoutUrl() {
  return axios.get(`${utils.apiBaseUrl()}/api/auth/logout`)
}

export function logOut() {
  return utils.get('/api/auth/logout')
}

export function updateUserSession(canvasCourseId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/auth/update_user_session`, {canvasCourseId})
}
