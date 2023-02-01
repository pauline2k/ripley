import _ from 'lodash'
import axios from 'axios'

export default {
  apiBaseUrl: () => import.meta.env.VITE_APP_API_BASE_URL,
  get: (path: string) => axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`).then(response => response.data),
  post: (path: string, data={}) => axios.post(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`, data).then(response => response.data),
  downloadViaGet(path: string, filename: string) {
    const fileDownload = require('js-file-download')
    return axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`).then(
        response => fileDownload(response.data, filename),
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
