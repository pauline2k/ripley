import utils from '@/api/api-utils'

export function setHypersleep(enabled: Boolean) {
  return utils.post('/api/config/hypersleep', {enabled}, true)
}
