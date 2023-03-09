import utils from '@/api/api-utils'

export function getJobHistory() {
  return utils.get('/api/job/history', true)
}

export function getJobSchedule() {
  return utils.get('/api/job/schedule', true)
}

export function getLastSuccessfulRun(jobKey: String) {
  return utils.get(`/api/job/${jobKey}/last_successful_run`, true)
}

export function setJobDisabled(jobId: String, disable: Boolean) {
  return utils.post('/api/job/disable', {disable, jobId}, true)
}

export function startJob(jobKey: String, params: Object) {
  return utils.post(`/api/job/${jobKey}/start`, params, true)
}

export function updateJobSchedule(jobId: String, type: String, value: String) {
  return utils.post('/api/job/schedule/update', {jobId, type, value}, true)
}
