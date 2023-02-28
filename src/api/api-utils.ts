import _ from 'lodash'
import axios from 'axios'

export default {
  apiBaseUrl: () => import.meta.env.VITE_APP_API_BASE_URL,
  get: (path: string) => axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`),
  post: (path: string, data={}) => axios.post(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`, data),
  downloadViaGet(path: string, filename: string) {
    const fileDownload = require('js-file-download')
    return axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`).then(
        data => fileDownload(data, filename),
        () => 'TODO: Vue.prototype.$errorHandler'
    )
  },
  termCodeToName(termCode: string) {
    return _.get(
      {
        'A': 'Winter',
        'B': 'Spring',
        'C': 'Summer',
        'D': 'Fall'
      },
      termCode
    )
  }
}
