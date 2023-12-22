import utils from '@/api/api-utils'

export function getUserProfile(uid: number) {
  return utils.post('/api/user/profile', {uid}, true)
}

export function getNostromoCrew() {
  return utils.get('/api/user/nostromo_crew')
}

export function searchUsers(searchText: string, searchType: string) {
  return utils.get(`/api/user/search?searchText=${searchText}&searchType=${searchType}`, false)
}
