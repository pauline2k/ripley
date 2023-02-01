import utils from './api-utils'

export function ping() {
  return utils.get('/api/ping')
}

export function getVersion() {
  return utils.get('/api/version')
}

export function getConfig() {
  return utils.get('/api/config')
}
