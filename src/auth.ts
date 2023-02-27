import router from './router'
import {useContextStore} from '@/stores/context'

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
  requiresAdmin: (to: any, from: any, next: any) => {
    const currentUser = useContextStore().currentUser
    if (currentUser.isAuthenticated) {
      if (currentUser.isAdmin) {
        next()
      } else {
        router.push({name: '404'})
      }
    } else {
      goToLogin(to, next)
    }
  }
}
