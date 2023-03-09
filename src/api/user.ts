import utils from '@/api/api-utils'

export function getUserProfile(uid: number) {
  return utils.post(`${utils.apiBaseUrl()}/api/user/profile`, {uid}, true)
}
