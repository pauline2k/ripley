import utils from '@/api/api-utils'

export function getUserProfile(uid: number) {
  return utils.post('/api/user/profile', {uid}, true)
}

export function getMyUserProfile() {
  return utils.get('/api/user/my_profile')
}
