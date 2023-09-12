import utils from '@/api/api-utils'
import {startsWith} from 'lodash'
import {useContextStore} from '@/stores/context'

const getTermName = (termId: string) => {
  const seasonCodes: any = {'0': 'Winter', '2': 'Spring', '5': 'Summer', '8': 'Fall'}
  const year = `${startsWith(termId, '1') ? 19 : 20}${termId.substring(1, 3)}`
  return `${seasonCodes[termId.substring(3, 4)]} ${year}`
}

export function downloadGradeCsv(
    gradeType: string,
    jobId: string,
    sectionId: string,
    termId: string
) {
  const currentUser = useContextStore().currentUser
  const termName = getTermName(termId).toLowerCase().replace(' ', '-')
  return utils.downloadViaGet(
    `/api/canvas_site/egrades_export/download?jobId=${jobId}`,
    `egrades-${gradeType}-${sectionId}-${termName}-${currentUser.canvasSiteId}.csv`,
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
