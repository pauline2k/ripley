import mitt from 'mitt'
import {defineStore} from 'pinia'
import {putFocusNextTick} from '@/utils'

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
    isLoading: false
  }),
  actions: {
    loadingComplete(focusTarget?: string) {
      this.isLoading = false
      putFocusNextTick(focusTarget || 'page-title')
    },
    loadingStart() {
      this.isLoading = true
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
