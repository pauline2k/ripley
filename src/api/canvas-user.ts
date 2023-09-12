import utils from '@/api/api-utils'

export function addUser(canvasSiteId: number, uid: string, sectionId: string, role: string) {
  return utils.post(`/api/canvas_user/${canvasSiteId}/users`, {uid, sectionId, role}, false)
}

export function getSections(canvasSiteId: number) {
  return utils.get(`/api/canvas_user/${canvasSiteId}/course_sections`, false)
}

export function getAddUserOptions(canvasSiteId: number) {
  return utils.get(`/api/canvas_user/${canvasSiteId}/options`, false)
}

export function searchUsers(searchText: string, searchType: string) {
  return utils.get(`/api/canvas_user/search?searchText=${searchText}&searchType=${searchType}`, false)
}
