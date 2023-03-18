import utils from '@/api/api-utils'
import moment from 'moment-timezone'

export function activateWelcomeEmail(canvasSiteId: string) {
  return utils.post(`/api/mailing_lists/${canvasSiteId}/welcome_email/activate`, true)
}

export function createMailingList(canvasSiteId: string, name: string, redirectOnError?: boolean) {
  return utils.post(`/api/mailing_lists/${canvasSiteId}/create`, {listName: name}, redirectOnError)
}

export function createSiteMailingList(canvasSiteId: string) {
  return utils.post(`/api/mailing_lists/${canvasSiteId}/create`, {}, true)
}

export function deactivateWelcomeEmail(canvasSiteId: string) {
  return utils.post(`/api/mailing_lists/${canvasSiteId}/welcome_email/deactivate`, {}, true)
}

export function downloadWelcomeEmailCsv(canvasSiteId: string) {
  const filename = `${canvasSiteId}-welcome-messages-log-${moment().format('YYYY-MM-DD_hhmmss')}.csv`
  return utils.downloadViaGet(`/api/mailing_lists/${canvasSiteId}/download/welcome_email_log`, filename,true)
}

export function getMailingList(canvasSiteId: string, redirectOnError?: boolean) {
  return utils.get(`/api/mailing_lists/${canvasSiteId}`, redirectOnError)
}

export function populateMailingList(canvasSiteId: string, redirectOnError?: boolean) {
  return utils.post(`/api/mailing_lists/${canvasSiteId}/populate`, {}, redirectOnError)
}

export function updateWelcomeEmail(canvasSiteId: string, subject: string, body: string) {
  return utils.post(`/api/mailing_lists/${canvasSiteId}/welcome_email/update`, {body, subject}, true)
}
