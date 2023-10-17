import {capitalize, concat, get, head, includes, initial, join, last, noop, startsWith, trim} from 'lodash'
import {nextTick} from 'vue'
import {useContextStore} from '@/stores/context'

export const isInIframe = !!window.parent.frames.length

export function decamelize(str: string, separator=' ') {
  const parsed = str.replace(/([a-z\d])([A-Z])/g, '$1' + separator + '$2')
  return capitalize(parsed.replace(/([A-Z]+)([A-Z][a-z\d]+)/g, '$1' + separator + '$2'))
}

export function getTermName(termId: string) {
  const seasonCodes: any = {'0': 'Winter', '2': 'Spring', '5': 'Summer', '8': 'Fall'}
  const year = `${startsWith(termId, '1') ? 19 : 20}${termId.substring(1, 3)}`
  return `${seasonCodes[termId.substring(3, 4)]} ${year}`
}

export function iframeParentLocation(location: string) {
  if (isInIframe) {
    const message = JSON.stringify(
      {
        subject: 'changeParent',
        parentLocation: location
      }
    )
    iframePostMessage(message)
  }
}

export function iframePostMessage(message: string) {
  if (window.parent) {
    window.parent.postMessage(message, '*')
  }
}

export function iframeScrollToTop() {
  if (isInIframe) {
    const message = JSON.stringify(
      {
        subject: 'changeParent',
        scrollToTop: true
      }
    )
    iframePostMessage(message)
  } else {
    window.scrollTo(0, 0)
  }
}

export function initializeAxios(app: any, axios: any) {
  const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
  const params = new URLSearchParams(window.location.search)
  if (params.get('canvasApiDomain')) {
    axios.defaults.headers['Ripley-Canvas-Api-Domain'] = params.get('canvasApiDomain')
  }
  axios.defaults.withCredentials = true
  axios.interceptors.response.use(
    (response: any) => response.headers['content-type'] === 'application/json' ? response.data : response,
    (error: any) => {
      const errorStatus = get(error, 'response.status')
      if (includes([401, 403], errorStatus)) {
        // Refresh user in case his/her session expired.
        return axios.get(`${apiBaseUrl}/api/user/my_profile`).then((data: any) => {
          const currentUser = data
          useContextStore().setCurrentUser(currentUser)
          if (!currentUser.isAuthenticated) {
            useContextStore().setApplicationState(errorStatus, 'Your session has expired')
          }
          return Promise.reject(error)
        })
      } else {
        return Promise.reject(error)
      }
    })
}

export function isValidCanvasSiteId(canvasSiteId: string) {
  canvasSiteId = trim(canvasSiteId)
  const maxValidCanvasSiteId = get(useContextStore(), 'config.maxValidCanvasSiteId') || 10
  return !!canvasSiteId && canvasSiteId.match(/^\d+$/) && parseInt(canvasSiteId, 10) <= maxValidCanvasSiteId
}

export function isValidCanvasUserId(canvasUserId: string) {
  canvasUserId = trim(canvasUserId)
  const maxValidCanvasSiteId = get(useContextStore(), 'config.maxValidCanvasSiteId') || 10
  return !!canvasUserId && canvasUserId.match(/^\d+$/) && parseInt(canvasUserId, 10) <= maxValidCanvasSiteId
}

export function isValidUID(uid: string) {
  uid = trim(uid)
  return !!uid && uid.match(/^\d+$/) && parseInt(uid, 10) <= 1000000
}

export function oxfordJoin(arr: any[]) {
  switch(arr.length) {
  case 0: return ''
  case 1: return head(arr)
  case 2: return `${head(arr)} and ${last(arr)}`
  default: return join(concat(initial(arr), ` and ${last(arr)}`), ', ')
  }
}

export function pluralize(noun: string, count: number, substitutions: any = {}, pluralSuffix: string = 's') {
  count = count || 0
  return (`${substitutions[count] || substitutions['other'] || count} ` + (count !== 1 ? `${noun}${pluralSuffix}` : noun))
}

export function printPage(filename: string) {
  const previousTitle = document.title
  document.title = filename
  window.print()
  document.title = previousTitle
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
  }).then(noop)
}

export function toInt(value: any, defaultValue: any = null) {
  const parsed = parseInt(value, 10)
  return Number.isInteger(parsed) ? parsed : defaultValue
}
