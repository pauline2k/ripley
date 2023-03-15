import utils from '@/api/api-utils'
import _ from 'lodash'

export function getCourseUserRoles(canvasCourseId: number) {
  return utils.get(`/api/course/${canvasCourseId}/user_roles`, true)
}

export function addUser(canvasCourseId: number, ldapUserId: string, sectionId: string, role: string) {
  return utils.post(`/api/course/${canvasCourseId}/add_user/add_user`, {ldapUserId, sectionId, role}, true)
}

export function getAddUserCourseSections(canvasCourseId: number) {
  return utils.get(`/api/course/${canvasCourseId}/add_user/course_sections`, true)
}

export function searchUsers(canvasCourseId: number, searchText: string, searchType: string) {
  return utils.get(`/api/course/${canvasCourseId}/add_user/search_users?searchText=${searchText}&searchType=${searchType}`, true)
}

export function downloadGradeCsv(canvasCourseId: number, ccn: string, termCode: string, termYear: string, type: string, pnpCutoff: string) {
  const queryParams = [
    `ccn=${ccn}`,
    `term_cd=${termCode}`,
    `term_yr=${termYear}`,
    `type=${type}`,
    `pnp_cutoff=${pnpCutoff}`
  ].join('&')
  const filename = `egrades-${type}-${ccn}-${utils.termCodeToName(termCode)}-${termYear}-${canvasCourseId}.csv`
  return utils.downloadViaGet(`/api/course/${canvasCourseId}/egrade_export/download?${queryParams}`, filename, true)
}

export function getExportOptions(canvasCourseId: number) {
  return utils.get(`/api/course/${canvasCourseId}/egrade_export/options`, true)
}

export function getExportJobStatus(canvasCourseId: number, jobId: string) {
  return utils.get(`/api/course/${canvasCourseId}/egrade_export/status?jobId=${jobId}`, true)
}

export function prepareGradesCacheJob(canvasCourseId: number) {
  return utils.post(`/api/course/${canvasCourseId}/egrade_export/prepare`, {}, true)
}

export function getCanvasSite(canvasCourseId: number) {
  return utils.get(`/api/course/${canvasCourseId}`, false)
}

export function getRoster(canvasCourseId: number) {
  return utils.get(`/api/course/${canvasCourseId}/roster`, true)
}

export function getRosterCsv(canvasCourseId: number) {
  return utils.downloadViaGet(
    `/api/course/${canvasCourseId}/roster_csv`,
    `course_${canvasCourseId}_rosters.csv`
  )
}

export function getCourseProvisioningMetadata() {
  return utils.get('/api/course/provision')
}

export function courseCreate(
  adminActingAs: string,
  adminByCcns: string[],
  adminTermSlug: string,
  ccns: string[],
  siteAbbreviation: string,
  siteName: string,
  termSlug: string
) {
  return utils.post('/api/course/provision/create', {
    admin_acting_as: adminActingAs,
    admin_by_ccns: adminByCcns,
    admin_term_slug: adminTermSlug,
    ccns,
    siteAbbreviation,
    siteName,
    termSlug
  })
}

export function createProjectSite(name: string) {
  return utils.post('/api/course/project_provision/create',{name})
}

export function courseProvisionJobStatus(jobId: number) {
  return utils.get(`/api/course/provision/status?jobId=${jobId}`)
}

export function getCourseSections(canvasCourseId: number) {
  return utils.get(`/api/course/${canvasCourseId}/provision/sections`)
}

export function getSections(
  adminActingAs: string,
  adminByCcns: number[],
  adminMode: string,
  currentSemester: string,
  isAdmin: boolean
) {
  let feedUrl = '/api/course/provision'
  if (isAdmin) {
    if (adminMode === 'act_as' && adminActingAs) {
      feedUrl = '/api/course/provision_as/' + adminActingAs
    } else if ((adminMode !== 'act_as') && adminByCcns) {
      feedUrl = `/api/course/provision?admin_term_slug=${currentSemester}`
      _.each(adminByCcns, ccn => feedUrl += `&admin_by_ccns[]=${ccn}`)
    }
  }
  return utils.get(feedUrl)
}

export function updateSiteSections(
  canvasCourseId: string,
  addCcns: string[],
  deleteCcns: string[],
  updateCcns: string[]
) {
  return utils.post(`/api/course/${canvasCourseId}/provision/edit_sections`, {
    ccns_to_remove: deleteCcns,
    ccns_to_add: addCcns,
    ccns_to_update: updateCcns
  })
}
