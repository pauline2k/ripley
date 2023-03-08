import _ from 'lodash'
import axios from 'axios'
import {useContextStore} from '@/stores/context'

const $_errorHandler = (error: any, redirectOnError?: boolean) => {
  const status = _.get(error, 'response.status')
  const message = $_getErrorMessage(error, status)
  if (redirectOnError) {
    useContextStore().setApplicationState(status, message)
  }
  return Promise.reject(message)
}

const $_getErrorMessage = (error: any, status: number) => {
  return useContextStore().currentUser.isAuthenticated && (!status || status >= 400)
    ? _.get(error, 'response.data.error') || _.get(error, 'response.data.message') || _.get(error, 'message')
    : 'Unauthorized request'
}

export default {
  apiBaseUrl: () => import.meta.env.VITE_APP_API_BASE_URL,
  get: (path: string, redirectOnError?: boolean) => {
    return axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`).then(
      data => data,
      error => $_errorHandler(error, redirectOnError)
    )
  },
  post: (path: string, data={}, redirectOnError?: boolean) => {
    return axios.post(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`, data).then(
      data => data,
      error => $_errorHandler(error, redirectOnError)
    )
  },
  downloadViaGet(path: string, filename: string, redirectOnError?: boolean) {
    const fileDownload = require('js-file-download')
    return axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`).then(
      data => fileDownload(data, filename),
      error => $_errorHandler(error, redirectOnError)
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
