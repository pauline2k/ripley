import _ from 'lodash'
import axios from 'axios'

export default {
  apiBaseUrl: () => 'TODO: Vue.prototype.$config.apiBaseUrl',
  get: (path: string) => axios.get(`${'TODO: Vue.prototype.$config.apiBaseUrl'}${path}`).then(response => response.data),
  post: (path: string, data={}) => axios.post(`${'TODO: Vue.prototype.$config.apiBaseUrl'}${path}`, data).then(response => response.data),
  downloadViaGet(path: string, filename: string) {
    const fileDownload = require('js-file-download')
    return axios.get(`${'TODO: Vue.prototype.$config.apiBaseUrl'}${path}`).then(
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
