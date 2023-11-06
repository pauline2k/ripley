import utils from '@/api/api-utils'

export function getGradeDistribution(canvasSiteId: number) {
  return utils.get(`/api/grade_distribution/${canvasSiteId}`)
}

export function searchCourses(searchText: string) {
  return utils.get(`/api/grade_distribution/search_courses?searchText=${searchText}`)
}
