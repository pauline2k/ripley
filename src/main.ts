import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import mitt from 'mitt'
import moment from 'moment'
import {createApp} from 'vue'
import {putFocusNextTick, axiosErrorHandler} from './utils'
import {registerPlugins} from '@/plugins'
import {useContextStore} from '@/stores/context'
import router from '@/router'

import './main.scss'

const app = createApp(App)
registerPlugins(app)

// Axios
const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
const params = new URLSearchParams(window.location.search)
if (params.get('canvasApiDomain')) {
  axios.defaults.headers['Ripley-Canvas-Api-Domain'] = params.get('canvasApiDomain')
}
axios.defaults.withCredentials = true

axios.interceptors.response.use(
  response => response.headers['content-type'] === 'application/json' ? response.data : response,
  error => {
    const errorStatus = _.get(error, 'response.status')
    if (_.includes([401, 403], errorStatus)) {
      // Refresh user in case his/her session expired.
      return axios.get(`${apiBaseUrl}/api/user/my_profile`).then(response => {
        useContextStore().setCurrentUser(response.data)
        const errorUrl = _.get(error, 'response.config.url')
        // Auth errors from the academics API should be handled by individual LTI components.
        if (!(errorUrl && errorUrl.includes('/api/academics'))) {
          axiosErrorHandler(app, error)
        }
        return Promise.reject(error)
      })
    } else {
      axiosErrorHandler(app, error)
      return Promise.reject(error)
    }
  })

// Global utilities
app.config.globalProperties.$_ = _
app.config.globalProperties.$errorHandler = axiosErrorHandler
app.config.globalProperties.$eventHub = mitt()
app.config.globalProperties.$loading = (label: string) => useContextStore().loadingStart(label)
app.config.globalProperties.$moment = moment
app.config.globalProperties.$ready = (label: string, focusTarget: string) => useContextStore().loadingComplete(label, focusTarget)
app.config.globalProperties.$putFocusNextTick = putFocusNextTick

axios.get(`${apiBaseUrl}/api/user/my_profile`).then(data => {
  useContextStore().setCurrentUser(data)

  axios.get(`${apiBaseUrl}/api/config`).then(data => {
    useContextStore().setConfig({
      ...data,
      apiBaseUrl,
      isVueAppDebugMode: _.trim(import.meta.env.VITE_APP_DEBUG).toLowerCase() === 'true'
    })
    app.use(router).config.errorHandler = function (error, vm, info) {
      useContextStore().setApplicationState(500, _.get(error, 'message') || info)
    }
    app.mount('#app')
  })
})
