import utils from '@/api/api-utils'

export function getGradeDistribution(canvasSiteId: number) {
  return utils.get(`/api/grade_distribution/${canvasSiteId}`)
}

export function getPriorEnrollmentGradeDistribution(canvasSiteId: number, courseName: string) {
  return utils.get(`/api/grade_distribution/${canvasSiteId}/enrollment?prior=${courseName}`)
}

export function searchCourses(searchText: string, abortController: AbortController) {
  return utils.getWithAbort(`/api/grade_distribution/search_courses?searchText=${searchText}`, abortController)
}
