import _ from 'lodash'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import auth from '@/auth'
import {app} from "@/main";

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
          title: 'MUTHUR'
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
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.afterEach((to: any) => {
  const title = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome'
  document.title = `${title} | Junction`
})

export default router
