import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import moment from 'moment'
import {createApp} from 'vue'
import {initializeAxios} from './utils'
import {registerPlugins} from '@/plugins'
import {useContextStore} from '@/stores/context'
import router from '@/router'

import './main.scss'

const app = createApp(App)

registerPlugins(app)
initializeAxios(app, axios)

// Globals
app.config.globalProperties.$_ = _
app.config.globalProperties.$moment = moment
app.config.globalProperties.$ready = (label: string, focusTarget?: string) => useContextStore().loadingComplete(label, focusTarget)

const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL

axios.get(`${apiBaseUrl}/api/user/my_profile`).then(data => {
  useContextStore().setCurrentUser(data)

  axios.get(`${apiBaseUrl}/api/config`).then(data => {
    useContextStore().setConfig({
      ...data,
      apiBaseUrl,
      isVueAppDebugMode: _.trim(import.meta.env.VITE_APP_DEBUG).toLowerCase() === 'true'
    })
    app.use(router).config.errorHandler = function (error, vm, info) {
      const message = _.get(error, 'message') || info || 'Uh oh, there was a problem.'
      const stacktrace = _.get(error, 'stack', null)
      console.log(`\n${message}\n${stacktrace}\n`)
      useContextStore().setApplicationState(500, message, stacktrace)
    }
    app.mount('#app')
  })
})
