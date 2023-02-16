import axios from '@/plugins/axios'
import type {App} from 'vue'
import VueAnnouncer from '@vue-a11y/announcer'
import vuetify from './vuetify'
import {createPinia} from 'pinia'
import {loadFonts} from './webfontloader'

export function registerPlugins (app: App) {
  loadFonts().then(() => {})
  app
    .use(axios, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
    .use(createPinia())
    .use(VueAnnouncer)
    .use(vuetify)
}
