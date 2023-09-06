import utils from '@/api/api-utils'

export function addUser(canvasSiteId: number, ldapUserId: string, sectionId: string, role: string) {
  return utils.post(`/api/canvas_user/${canvasSiteId}/add`, {ldapUserId, sectionId, role}, true)
}

export function getSections(canvasSiteId: number) {
  return utils.get(`/api/canvas_user/${canvasSiteId}/course_sections`, false)
}

export function getAddUserOptions(canvasSiteId: number) {
  return utils.get(`/api/canvas_user/${canvasSiteId}/options`, true)
}

export function searchUsers(searchText: string, searchType: string) {
  return utils.get(`/api/canvas_user/search?searchText=${searchText}&searchType=${searchType}`, false)
}
