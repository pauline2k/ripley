import axios from 'axios'
import utils from '@/api/api-utils'

export function getUserProfile(uid: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/user/profile`, {uid})
}
