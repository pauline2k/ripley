import axios from 'axios'
import fileDownload from 'js-file-download'
import {get} from 'lodash'
import {useContextStore} from '@/stores/context'

const $_errorHandler = (error: any, redirectOnError?: boolean) => {
  if (axios.isCancel(error)) {
    return Promise.reject('Operation Canceled')
  } else {
    const status = get(error, 'response.status')
    const message = get(error, 'response.data.error') || get(error, 'response.data.message') || get(error, 'message') || 'Unauthorized'
    // eslint-disable-next-line no-console
    console.log(`\n${error}\n${message}\n`)
    if (redirectOnError) {
      useContextStore().setApplicationState(status, message)
    }
    return Promise.reject(message)
  }
}

export default {
  apiBaseUrl: () => import.meta.env.VITE_APP_API_BASE_URL,
  get: function<T>(path: string, redirectOnError?: boolean): Promise<T> {
    return axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`).then(
      data => data as T,
      error => $_errorHandler(error, redirectOnError)
    )
  },
  getWithAbort: (path: string, abortController: AbortController, redirectOnError?: boolean) => {
    return axios.get(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`, {
      signal: abortController.signal
    }).then(
      data => data,
      error => $_errorHandler(error, redirectOnError)
    )
  },
  post: function<T>(path: string, data={}, redirectOnError?: boolean): Promise<T> {
    return axios.post(`${import.meta.env.VITE_APP_API_BASE_URL}${path}`, data).then(
      data => data as T,
      error => $_errorHandler(error, redirectOnError)
    )
  },
  downloadViaGet(path: string, filename: string, redirectOnError?: boolean) {
    // Filename prefix is intended for developer workstation only. Set its value in the ".env.development.local" file.
    // The prefix in filename will distinguish local downloads, useful when comparing results with other environments.
    const prefix = import.meta.env.VITE_APP_DOWNLOAD_FILENAME_PREFIX
    filename = `${prefix}${filename}`
    return axios(
      `${import.meta.env.VITE_APP_API_BASE_URL}${path}`,
      {responseType: 'blob'}
    ).then(
      (response: any) => fileDownload(response.data, filename),
      error => $_errorHandler(error, redirectOnError)
    )
  }
}
