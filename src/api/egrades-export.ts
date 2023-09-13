import utils from '@/api/api-utils'

export function downloadGradeCsv(filename: string, jobId: string) {
  return utils.downloadViaGet(
    `/api/canvas_site/egrades_export/download?jobId=${jobId}`,
    filename,
    true
  )
}

export function getExportOptions(redirectOnError?: boolean) {
  return utils.get('/api/canvas_site/egrades_export/options', redirectOnError)
}

export function getExportJobStatus(jobId: string) {
  return utils.post('/api/canvas_site/egrades_export/status', {jobId}, false)
}

export function prepareGradesCacheJob(
  gradeType: string,
  pnpCutoff: string,
  sectionId: string,
  termId: string
) {
  const data = {gradeType, pnpCutoff, sectionId, termId}
  return utils.post('/api/canvas_site/egrades_export/prepare', data, false)
}
