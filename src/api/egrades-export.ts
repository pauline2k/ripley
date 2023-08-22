import _ from 'lodash'
import utils from '@/api/api-utils'
import {useContextStore} from '@/stores/context'

const getTermName = (termId: string) => {
  const seasonCodes: any = {'0': 'Winter', '2': 'Spring', '5': 'Summer', '8': 'Fall'}
  const year = `${_.startsWith(termId, '1') ? 19 : 20}${termId.substring(1, 3)}`
  return `${seasonCodes[termId.substring(3, 4)]} ${year}`
}

export function downloadGradeCsv(
    gradeType: string,
    sectionId: string,
    termId: string,
    pnpCutoff: string
) {
  const currentUser = useContextStore().currentUser
  const queryParams = [
    `gradeType=${gradeType}`,
    `pnpCutoff=${pnpCutoff}`,
    `sectionId=${sectionId}`,
    `termId=${termId}`
  ].join('&')
  const termName = getTermName(termId).toLowerCase().replace(' ', '-')
  return utils.downloadViaGet(
    `/api/canvas_site/egrades_export/download?${queryParams}`,
    `egrades-${gradeType}-${sectionId}-${termName}-${currentUser.canvasSiteId}.csv`,
    true
  )
}

export function getExportOptions(redirectOnError?: boolean) {
  return utils.get('/api/canvas_site/egrades_export/options', redirectOnError)
}

export function getExportJobStatus(jobId: string) {
  return utils.post('/api/canvas_site/egrades_export/status', {jobId}, true)
}

export function prepareGradesCacheJob() {
  return utils.post('/api/canvas_site/egrades_export/prepare', {}, true)
}
