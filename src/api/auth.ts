import axios from 'axios'
import utils from './api-utils'

export function devAuthLogIn(uid: string, password: string) {
  const url = `${utils.apiBaseUrl()}/api/auth/dev_auth`
  return axios.post(url, {
    password,
    uid
  }).then(response => {
    if (response.data.isLoggedIn) {
      // TODO: Vue.prototype.$currentUser = response.data
    }
    return response.data
  })
}

export function logOut() {
  return utils.get('/logout')
}
