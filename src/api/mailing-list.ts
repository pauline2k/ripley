import utils from '@/api/api-utils'
import moment from 'moment-timezone'

export function activateWelcomeEmail(canvasCourseId: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/welcome_email/activate`, true)
}

export function createMailingList(canvasCourseId: string, name: string, redirectOnError?: boolean) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/create`, {listName: name}, redirectOnError)
}

export function createSiteMailingList(canvasCourseId: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/create`, {}, true)
}

export function deactivateWelcomeEmail(canvasCourseId: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/welcome_email/deactivate`, {}, true)
}

export function downloadWelcomeEmailCsv(canvasCourseId: string) {
  const filename = `${canvasCourseId}-welcome-messages-log-${moment().format('YYYY-MM-DD_hhmmss')}.csv`
  return utils.downloadViaGet(`/api/mailing_lists/${canvasCourseId}/download/welcome_email_log`, filename,true)
}

export function getMailingList(canvasCourseId: string, redirectOnError?: boolean) {
  return utils.get(`/api/mailing_lists/${canvasCourseId}`, redirectOnError)
}

export function populateMailingList(canvasCourseId: string, redirectOnError?: boolean) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/populate`, {}, redirectOnError)
}

export function updateWelcomeEmail(canvasCourseId: string, subject: string, body: string) {
  return utils.post(`/api/mailing_lists/${canvasCourseId}/welcome_email/update`, {body, subject}, true)
}
