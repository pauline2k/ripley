import mitt from 'mitt'
import {defineStore} from 'pinia'
import {nextTick} from 'vue'
import {noop} from 'lodash'
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
      if (focusTarget) {
        putFocusNextTick(focusTarget)
      } else {
        const callable = () => {
          const elements = document.getElementsByTagName('h1')
          if (elements.length > 0) {
            elements[0].setAttribute('tabindex', '-1')
            elements[0].focus()
          }
          return elements.length > 0
        }
        nextTick(() => {
          let counter = 0
          const job: any = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
        }).then(noop)
      }
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
