import utils from '@/api/api-utils'

export function externalTools() {
  return utils.get('/api/canvas/external_tools', true)
}

export function getSiteCreationAuthorizations() {
  return utils.get('/api/canvas/authorizations', true)
}

export function canUserCreateSite() {
  return utils.get('/api/canvas/can_user_create_site', true)
}

export function importUsers(userIds: string[]) {
  return utils.post('/api/canvas/user_provision/user_import', {userIds}, true)
}
