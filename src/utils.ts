import _ from 'lodash'
import mitt from 'mitt'
import router from './router'
import {App, nextTick} from 'vue'

export function axiosErrorHandler(error: any) {
  const errorStatus = _.get(error, 'response.status')
  const currentUser = undefined // TODO: The old way was Vue.prototype.$currentUser.
  if (_.get(currentUser, 'isAuthenticated')) {
    if (!errorStatus || errorStatus >= 400) {
      const message = _.get(error, 'response.data.error') || _.get(error, 'response.data.message') || error.message
      router.push({
        path: '/error',
        query: {
          m: message
        }
      })
    } else if (errorStatus === 404) {
      router.push({path: '/404'})
    }
  } else {
    router.push({
      path: '/login',
      query: {
        m: 'Your session has expired'
      }
    })
  }
}

export function putFocusNextTick(id: string, cssSelector?: string) {
  const callable = () => {
    let el = document.getElementById(id)
    el = el && cssSelector ? el.querySelector(cssSelector) : el
    el && el.focus()
    return !!el
  }
  nextTick(() => {
    let counter = 0
    const job:any = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
  }).then(_.noop)
}
