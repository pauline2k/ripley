import _ from 'lodash'
import Default from '@/layouts/default/Default.vue'
import Error from '@/views/Error.vue'
import Login from '@/views/Login.vue'
import Jobs from '@/views/Jobs.vue'
import NotFound from '@/views/NotFound.vue'
import Welcome from '@/views/Welcome.vue'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import auth from '@/auth'
import {app} from '@/main'

const routes:RouteRecordRaw[] = [
  {
    path: '/',
    beforeEnter: (to: any, from: any, next: any) => {
      const currentUser = app.config.globalProperties.$currentUser
      currentUser.isAuthenticated
          ? (currentUser.isAdmin
              ? next({path: '/jobs'})
              : next({path: '/welcome'}))
          : next()
    },
    component: Default,
    children: [
      {
        path: '',
        name: 'Login',
        // Lazy-load components
        component: Login
      }
    ]
  },
    {
    path: '/',
    beforeEnter: auth.requiresAdmin,
    component: Default,
    children: [
      {
        path: '/welcome',
        name: 'Welcome',
        // Lazy-load components
        component: Welcome
      },
      {
        path: '/jobs',
        component: Jobs,
        meta: {
          title: 'MU-TH-UR 6000'
        }
      }
    ]
  },
  {
    path: '/',
    component: Default,
    children: [
      {
        beforeEnter: (to: any, from: any, next: any) => {
          to.params.m = to.redirectedFrom
          next()
        },
        path: '/404',
        component: NotFound,
        meta: {
          title: 'Page not found'
        }
      },
      {
        path: '/error',
        component: Error,
        meta: {
          title: 'Error'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to: any) => {
  const title = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome'
  document.title = `${title} | UC Berkeley`
})

export default router
