import mitt from 'mitt'
import {defineStore} from 'pinia'
import {get} from 'lodash'
import {nextTick} from 'vue'
import {putFocusNextTick} from '@/utils'
import router from '@/router'

export type RipleyConfig = {
  canvasApiUrl: string,
  casLogoutUrl: string,
  devAuthEnabled: boolean,
  hypersleep: any,
  newtInformationBlock: string,
  newtShowOtherGender: boolean,
  terms: {
    current: {
      name: string
    },
    next: {
      name: string
    }
  }
}

export type RipleyUser = {
  canAccessStandaloneView: boolean,
  canvasSiteId: number,
  canvasSiteName: string | undefined,
  inDemoMode: boolean,
  isAdmin: boolean,
  isAuthenticated: boolean,
  isCanvasAdmin: boolean,
  uid: string | undefined
}

const $_getDefaultApplicationState = () => ({
  message: undefined,
  stacktrace: undefined,
  status: 200
})

const ANONYMOUS_USER: RipleyUser = {
  canAccessStandaloneView: false,
  canvasSiteId: NaN,
  canvasSiteName: undefined,
  inDemoMode: false,
  isAdmin: false,
  isAuthenticated: false,
  isCanvasAdmin: false,
  uid: undefined
}

export const useContextStore = defineStore('context', {
  state: () => ({
    applicationState: $_getDefaultApplicationState(),
    config: {} as RipleyConfig,
    currentUser: ANONYMOUS_USER as RipleyUser,
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
      const route = router.currentRoute
      if (!get(route, 'value.meta.announcer.skip')) {
        const name = String(get(route, 'value.name', ''))
        this.alertScreenReader(`${name} page has loaded.`, 'polite')
      }
      nextTick(() => {
        setTimeout(() => putFocusNextTick(focusTarget || 'page-title'), 150)
      })
    },
    loadingStart(route?: object) {
      this.isLoading = true
      if (!get(route, 'meta.announcer.skip')) {
        const name = String(get(route, 'name', ''))
        this.alertScreenReader(`${name} page is loading.`, 'polite')
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
    },
    setHypersleep(hypersleep: any) {
      this.config.hypersleep = hypersleep
    }
  }
})
