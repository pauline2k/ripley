import utils from '@/api/api-utils'

export function getUserProfile(uid: number) {
  return utils.post('/api/user/profile', {uid}, true)
}
