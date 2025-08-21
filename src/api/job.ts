import {Job, JobRunSummary} from '@/lib/types'
import utils from '@/api/api-utils'

export function getJobHistory() {
  return utils.get<JobRunSummary>('/api/job/history', true)
}

export function getJobSchedule() {
  return utils.get('/api/job/schedule', true)
}

export function getLastSuccessfulRun(jobKey: string) {
  return utils.get(`/api/job/${jobKey}/last_successful_run`, true)
}

export function setJobDisabled(jobId: string, disable: boolean) {
  return utils.post<Job>('/api/job/disable', {disable, jobId}, true)
}

export function startJob(jobKey: string, params: object) {
  return utils.post(`/api/job/${jobKey}/start`, params, true)
}

export function updateJobSchedule(jobId: string, type: string, value: string) {
  return utils.post('/api/job/schedule/update', {jobId, type, value}, true)
}
