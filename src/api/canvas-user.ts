import utils from '@/api/api-utils'

export function addUser(canvasSiteId: number, ldapUserId: string, sectionId: string, role: string) {
  return utils.post(`/api/canvas_user/${canvasSiteId}/add`, {ldapUserId, sectionId, role}, true)
}

export function getAddUserCourseSections(canvasSiteId: number) {
  return utils.get(`/api/canvas_user/${canvasSiteId}/course_sections`, true)
}

export function getCanvasSiteUserRoles(canvasSiteId: number) {
  return utils.get(`/api/canvas_user/${canvasSiteId}/roles`, true)
}

export function searchUsers(canvasSiteId: number, searchText: string, searchType: string) {
  return utils.get(`/api/canvas_user/${canvasSiteId}/search?searchText=${searchText}&searchType=${searchType}`, true)
}
