import {app} from './main'
import axios from 'axios'

const goToLogin = (to: any, next: any) => {
  next({
    path: '/',
    query: {
      error: to.query.error,
      redirect: to.fullPath
    }
  })
}

export default {
  initSession: (currentUser: Object) => {
    return new Promise<void>(resolve => {
      const apiBaseUrl = import.meta.env.VITE_APP_API_BASE_URL
        app.config.globalProperties.$currentUser = currentUser
        // Set Axios CSRF headers for non-GET requests
        axios.defaults.headers.post['X-CSRF-Token'] = response.data.csrfToken
        axios.defaults.headers.put['X-CSRF-Token'] = response.data.csrfToken
        axios.defaults.headers.delete['X-CSRF-Token'] = response.data.csrfToken
        resolve()
    })
  },
  requiresAdmin: (to: any, from: any, next: any) => {
    const currentUser = app.config.globalProperties.$currentUser
    if (currentUser.isAuthenticated) {
      if (currentUser.isAdmin) {
        next()
      } else {
        next({path: '/404'})
      }
    } else {
      goToLogin(to, next)
    }
  },
  requiresAuthenticated: (to: any, from: any, next: any) => {
    const currentUser = {isAuthenticated: false} // TODO: app.config.globalProperties.$currentUser
    if (currentUser.isAuthenticated) {
      next()
    } else {
      goToLogin(to, next)
    }
  }
}
