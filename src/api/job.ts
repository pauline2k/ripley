import utils from '@/api/api-utils'

export function getJobHistory() {
  return utils.get('/api/job/history')
}

export function getJobSchedule() {
  return utils.get('/api/job/schedule')
}

export function getLastSuccessfulRun(jobKey: String) {
  return utils.get(`/api/job/${jobKey}/last_successful_run`)
}

export function setJobDisabled(jobId: String, disable: Boolean) {
  return utils.post('/api/job/disable', {
    jobId,
    disable
  })
}

export function startJob(jobKey: String, params: Object) {
  return utils.post(`/api/job/${jobKey}/start`, params)
}

export function updateJobSchedule(jobId: String, type: String, value: String) {
  return utils.post('/api/job/schedule/update', {
    jobId,
    type,
    value
  })
}
