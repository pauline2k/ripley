import _ from 'lodash'
import moment from 'moment-timezone'
import utils from '@/api/api-utils'

export function getGradeDistribution(canvasSiteId: number) {
  return utils.get(`/api/canvas_site/${canvasSiteId}/grade_distribution`, true)
}

export function getCanvasSite(canvasSiteId: number, includeUsers?: boolean, redirectOnError?: boolean) {
  return utils.get(`/api/canvas_site/${canvasSiteId}?includeUsers=${!!includeUsers}`, redirectOnError)
}

export function getRoster(canvasSiteId: number, redirectOnError?: boolean) {
  return utils.get(`/api/canvas_site/${canvasSiteId}/roster`, redirectOnError)
}

export function exportRoster(canvasSiteId: number) {
  return utils.downloadViaGet(
    `/api/canvas_site/${canvasSiteId}/export_roster`,
    `course_${canvasSiteId}_rosters-${moment().format('YYYY-MM-DD_hhmmss')}.csv`
  )
}

export function getCourseProvisioningMetadata() {
  return utils.get('/api/canvas_site/provision')
}

export function courseCreate(
  adminActingAs: string,
  adminBySectionIds: string[],
  adminTermSlug: string,
  sectionIds: string[],
  siteAbbreviation: string,
  siteName: string,
  termSlug: string
) {
  return utils.post('/api/canvas_site/provision/create', {
    adminActingAs: adminActingAs,
    adminBySectionIds: adminBySectionIds,
    adminTermSlug: adminTermSlug,
    sectionIds,
    siteAbbreviation,
    siteName,
    termSlug
  })
}

export function createProjectSite(name: string) {
  return utils.post('/api/canvas_site/project_provision/create',{name})
}

export function courseProvisionJobStatus(jobId: number) {
  return utils.get(`/api/canvas_site/provision/status?jobId=${jobId}`)
}

export function getCourseSections(canvasSiteId: number) {
  return utils.get(`/api/canvas_site/${canvasSiteId}/provision/sections`, true)
}

export function getSections(
  adminActingAs: string,
  adminBySectionIds: number[],
  adminMode: string,
  currentSemester: string,
  isAdmin: boolean
) {
  let feedUrl = '/api/canvas_site/provision'
  if (isAdmin) {
    if (adminMode === 'act_as' && adminActingAs) {
      feedUrl = '/api/canvas_site/provision_as/' + adminActingAs
    } else if ((adminMode !== 'act_as') && adminBySectionIds) {
      feedUrl = `/api/canvas_site/provision?admin_term_slug=${currentSemester}`
      _.each(adminBySectionIds, sectionId => feedUrl += `&adminBySectionIds[]=${sectionId}`)
    }
  }
  return utils.get(feedUrl)
}

export function updateSiteSections(
  canvasSiteId: string,
  sectionIdsToAdd: string[],
  sectionIdsToRemove: string[],
  sectionIdsToUpdate: string[]
) {
  return utils.post(`/api/canvas_site/${canvasSiteId}/provision/sections`, {
    sectionIdsToAdd,
    sectionIdsToRemove,
    sectionIdsToUpdate
  })
}
