import _ from 'lodash'
import {nextTick} from 'vue'
import {putFocusNextTick} from '@/utils'
import {defineStore} from 'pinia'

export const useContextStore = defineStore('context', {
  state: () => ({
    isLoading: false,
  }),
  actions: {
    loadingComplete(label?: string, focusTarget?: string) {
      document.title = `${label || 'bCourses'} | UC Berkeley`
      this.isLoading = false
      if (label) {
        // TODO: use '@vue-a11y/announcer' instead
        // state.screenReaderAlert = `${label} page is ready`
      }
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
        }).then(_.noop)
      }
    },
    loadingStart(label?: string) {
      this.isLoading = true
      // TODO: use '@vue-a11y/announcer' instead
      // state.screenReaderAlert = `${label || 'Page'} is loading...`
    }
  }
})
