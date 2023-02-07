import _ from 'lodash'
import auth from '@/auth'
import {app} from '@/main'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'

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
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        path: '',
        name: 'Login',
        // Lazy-load components
        component: () => import('@/views/Login.vue')
      }
    ]
  },
    {
    path: '/',
    beforeEnter: auth.requiresAdmin,
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        path: '/welcome',
        name: 'Welcome',
        // Lazy-load components
        component: () => import('@/views/Welcome.vue')
      },
      {
        path: '/jobs',
        component: () => import('@/views/Jobs.vue'),
        meta: {
          title: 'MU-TH-UR 6000'
        }
      }
    ]
  },
  {
    path: '/',
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        beforeEnter: (to: any, from: any, next: any) => {
          to.params.m = to.redirectedFrom
          next()
        },
        path: '/404',
        component: () => import('@/views/NotFound.vue'),
        meta: {
          title: 'Page not found'
        }
      },
      {
        path: '/error',
        component: () => import('@/views/Error.vue'),
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
