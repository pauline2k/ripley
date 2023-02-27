import _ from 'lodash'
import {nextTick} from 'vue'
import {useContextStore} from '@/stores/context'

export function axiosErrorHandler(app: any, error: any) {
  const status = _.get(error, 'response.status')
  const message = useContextStore().currentUser.isAuthenticated && (!status || status >= 400)
    ? _.get(error, 'response.data.error') || _.get(error, 'response.data.message') || error.message
    : 'Your session has expired'
  useContextStore().setApplicationState(status, message)
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
