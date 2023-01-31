import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import { registerUtils } from './utils'
import { createApp } from 'vue'
import { registerPlugins } from '@/plugins'

const app = createApp(App)

registerPlugins(app)
registerUtils(app)

const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
const isDebugMode = _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true'

axios.get(`${apiBaseUrl}/api/config`).then(response => {
  app.config.globalProperties.$config = {...response.data, apiBaseUrl, isVueAppDebugMode: isDebugMode}
  app.mount('#app')
})
