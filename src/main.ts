import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import mitt from 'mitt'
import moment from 'moment'
import router from '@/router'
import {putFocusNextTick, axiosErrorHandler} from './utils'
import {createApp} from 'vue'
import {registerPlugins} from '@/plugins'
import {useContextStore} from '@/stores/context'

export const app = createApp(App)

registerPlugins(app)

// Axios
const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
axios.defaults.withCredentials = true

axios.interceptors.response.use(
  response => response,
  error => {
    const errorStatus = _.get(error, 'response.status')
    if (_.includes([401, 403], errorStatus)) {
      // Refresh user in case his/her session expired.
      return axios.get(`${apiBaseUrl}/api/my/status`).then(response => {
        app.config.globalProperties.$currentUser = response.data
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

// Global utilities
const contextStore: any = useContextStore()
app.config.globalProperties.$_ = _
app.config.globalProperties.$errorHandler = axiosErrorHandler
app.config.globalProperties.$eventHub = mitt()
app.config.globalProperties.$loading = (label: string) => contextStore.loadingStart(label)
app.config.globalProperties.$moment = moment
app.config.globalProperties.$ready = (label: string, focusTarget: string) => contextStore.loadingComplete(label, focusTarget)
app.config.globalProperties.$putFocusNextTick = putFocusNextTick

axios.get(`${apiBaseUrl}/api/user/my_profile`).then(response => {
  app.config.globalProperties.$currentUser = response.data
  app.use(router)

  axios.get(`${apiBaseUrl}/api/config`).then(response => {
    const isDebugMode = _.trim(import.meta.env.VUE_APP_DEBUG).toLowerCase() === 'true'
    app.config.globalProperties.$config = {...response.data, apiBaseUrl, isVueAppDebugMode: isDebugMode}
    app.mount('#app')
  })
})
