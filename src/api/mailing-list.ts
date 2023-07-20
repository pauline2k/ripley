import moment from 'moment-timezone'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

export function activateWelcomeEmail() {
  return utils.post('/api/mailing_list/welcome_email/activate', true)
}

export function createMailingList(name: string, redirectOnError?: boolean) {
  return utils.post('/api/mailing_list/create', {name}, redirectOnError)
}

export function deactivateWelcomeEmail() {
  return utils.post('/api/mailing_list/welcome_email/deactivate', {}, true)
}

export function downloadWelcomeEmailCsv() {
  const currentUser = useContextStore().currentUser
  const filename = `${currentUser.canvasSiteId}-welcome-messages-log-${moment().format('YYYY-MM-DD_hhmmss')}.csv`
  return utils.downloadViaGet('/api/mailing_list/download/welcome_email_log', filename,true)
}

export function getSuggestedMailingListName() {
  return utils.get('/api/mailing_list/suggested_name', true)
}

export function getMyMailingList(redirectOnError?: boolean) {
  return utils.get('/api/mailing_list/my', redirectOnError)
}

export function populateMailingList(redirectOnError?: boolean) {
  return utils.post('/api/mailing_list/populate', {}, redirectOnError)
}

export function updateWelcomeEmail(active: boolean, body: string, subject: string) {
  return utils.post('/api/mailing_list/welcome_email/update', {active, body, subject}, true)
}
