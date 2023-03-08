import utils from '@/api/api-utils'
import moment from 'moment-timezone'

export function activateWelcomeEmail(canvasCourseId: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/welcome_email/activate`, true)
}

export function createSiteMailingList(canvasCourseId: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/create`, {}, true)
}

export function deactivateWelcomeEmail(canvasCourseId: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/welcome_email/deactivate`, {}, true)
}

export function downloadWelcomeEmailCsv(canvasCourseId: string) {
  const filename = `${canvasCourseId}-welcome-messages-log-${moment().format('YYYY-MM-DD_hhmmss')}.csv`
  return utils.downloadViaGet(`/api/mailing_lists/${canvasCourseId}/welcome_email_log`, filename,true)
}

export function getSiteMailingList(canvasCourseId: string) {
  return utils.get(`/api/mailing_lists/${canvasCourseId}`, true)
}

export function updateWelcomeEmail(canvasCourseId: string, subject: string, body: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/welcome_email/update`, {body, subject}, true)
}

export function getSiteMailingListAdmin(canvasCourseId: string, redirectOnError?: boolean) {
  return utils.get(`/api/mailing_lists/${canvasCourseId}`, redirectOnError)
}

export function createSiteMailingListAdmin(canvasCourseId: string, name: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/create`, {listName: name}, true)
}

export function populateSiteMailingList(canvasCourseId: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/populate`, {}, true)
}
