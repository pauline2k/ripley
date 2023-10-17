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

export function getCanvasUserProfileById(canvasUserId: number) {
  return utils.get(`/api/canvas_user/${canvasUserId}`, false)
}

export function getCanvasUserProfileByUID(uid: number) {
  return utils.get(`/api/canvas_user/by_uid/${uid}`, false)
}

export function getCanvasSiteUserProfile(canvasSiteId: number, canvasUserId: number) {
  return utils.get(`/api/canvas_user/${canvasUserId}/canvas_site/${canvasSiteId}`, false)
}
