import _ from 'lodash'
import {nextTick} from 'vue'
import {useContextStore} from '@/stores/context'

export function initializeAxios(app: any, axios: any) {
  const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
  const params = new URLSearchParams(window.location.search)
  if (params.get('canvasApiDomain')) {
    axios.defaults.headers['Ripley-Canvas-Api-Domain'] = params.get('canvasApiDomain')
  }
  axios.defaults.withCredentials = true
  axios.interceptors.response.use(
    (response: any) => response.headers['content-type'] === 'application/json' ? response.data : response,
    (error: any) => {
      const errorStatus = _.get(error, 'response.status')
      if (_.includes([401, 403], errorStatus)) {
        // Refresh user in case his/her session expired.
        return axios.get(`${apiBaseUrl}/api/user/my_profile`).then((response: any) => {
          useContextStore().setCurrentUser(response.data)
          const errorUrl = _.get(error, 'response.config.url')
          // Auth errors from the academics API should be handled by individual LTI components.
          if (!(errorUrl && errorUrl.includes('/api/academics'))) {
            axiosErrorHandler(error)
          }
          return Promise.reject(error)
        })
      } else {
        axiosErrorHandler(error)
        return Promise.reject(error)
      }
    })
}

export function axiosErrorHandler(error: any) {
  const status = _.get(error, 'response.status')
  const message = useContextStore().currentUser.isAuthenticated && (!status || status >= 400)
    ? _.get(error, 'response.data.error') || _.get(error, 'response.data.message') || _.get(error, 'message')
    : 'Your session has expired'
  useContextStore().setApplicationState(status, message)
}

export function putFocusNextTick(id: string, cssSelector?: string) {
  const callable = () => {
    let el = document.getElementById(id)
    el = el && cssSelector ? el.querySelector(cssSelector) : el
    el && el.focus()
    return !!el
  }
  nextTick(() => {
    let counter = 0
    const job:any = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
  }).then(_.noop)
}
