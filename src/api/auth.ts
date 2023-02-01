import axios from 'axios'
import utils from './api-utils'

export function devAuthLogIn(uid: string, password: string) {
  const url = `${utils.apiBaseUrl()}/api/auth/dev_auth`
  return axios.post(url, {
    password,
    uid
  }).then(response => {
    if (response.data.isAuthenticated) {
      // TODO: Vue.prototype.$currentUser = response.data
    }
    return response.data
  })
}

export function getCasLoginURL() {
  return utils.get(`/api/auth/cas_login_url`)
}

export function getCasLogoutUrl() {
  return axios.get(`${utils.apiBaseUrl()}/api/auth/logout`)
}

export function logOut() {
  return utils.get('/api/auth/logout')
}
