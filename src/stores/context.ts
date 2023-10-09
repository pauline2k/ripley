import mitt from 'mitt'
import {defineStore} from 'pinia'
import {get} from 'lodash'
import {nextTick} from 'vue'
import {putFocusNextTick} from '@/utils'
import {useRoute} from 'vue-router'



const $_getDefaultApplicationState = () => ({
  message: undefined,
  stacktrace: undefined,
  status: 200
})

export const useContextStore = defineStore('context', {
  state: () => ({
    applicationState: $_getDefaultApplicationState(),
    config: undefined,
    currentUser: {
      canvasSiteId: undefined,
      isAdmin: false,
      isAuthenticated: false
    },
    eventHub: mitt(),
    isLoading: false,
    screenReaderAlert: {
      message: '',
      politeness: 'polite'
    }
  }),
  actions: {
    alertScreenReader(message: string, politeness?: string) {
      this.screenReaderAlert.message = ''
      nextTick(() => {
        this.screenReaderAlert = {
          message: message,
          politeness: politeness || 'polite'
        }
      })
    },
    loadingComplete(focusTarget?: string) {
      this.isLoading = false
      const route = useRoute()
      if (!get(route, 'meta.announcer.skip')) {
        this.screenReaderAlert.message = `${String(get(route, 'name', ''))} page has loaded.`
      }
      putFocusNextTick(focusTarget || 'page-title')
    },
    loadingStart() {
      this.isLoading = true
      const route = useRoute()
      if (!get(route, 'meta.announcer.skip')) {
        this.screenReaderAlert.message = `${String(get(route, 'name', ''))} page is loading.`
      }
    },
    resetApplicationState() {
      this.applicationState = $_getDefaultApplicationState()
    },
    setConfig(config: any) {
      this.config = config
    },
    setApplicationState(status: number, message?: any, stacktrace?: any) {
      this.applicationState = {message, stacktrace, status}
    },
    setCurrentUser(user: any) {
      this.currentUser = user
      this.eventHub.emit('current-user-update')
    }
  }
})
