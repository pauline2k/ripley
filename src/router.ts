import _ from 'lodash'
import auth from '@/auth'
import {app} from '@/main'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import {defineAsyncComponent} from 'vue'

const routes:RouteRecordRaw[] = [
  {
    beforeEnter: (to: any, from: any, next: any) => {
      const currentUser = app.config.globalProperties.$currentUser
      currentUser.isAuthenticated ? (currentUser.isAdmin ? next({path: '/jobs'}) : next({path: '/welcome'})) : next()
    },
    children: [
      {
        component: defineAsyncComponent(() => import('@/views/Login.vue')),
        name: 'Login',
        path: '',
      }
    ],
    component: () => defineAsyncComponent(() => import('@/layouts/default/Default.vue')),
    path: '/',
  },
    {
    beforeEnter: auth.requiresAdmin,
    children: [
      {
        component: () => defineAsyncComponent(() => import('@/views/Welcome.vue')),
        name: 'Welcome',
        path: '/welcome',
      },
      {
        path: '/jobs',
        component: () => defineAsyncComponent(() => import('@/views/Jobs.vue')),
        meta: {title: 'MU-TH-UR 6000'}
      }
    ],
    component: () => defineAsyncComponent(() => import('@/layouts/default/Default.vue')),
    path: '/',
  },
  {
    children: [
      {
        beforeEnter: (to: any, from: any, next: any) => {
          to.params.m = to.redirectedFrom
          next()
        },
        path: '/404',
        component: () => defineAsyncComponent(() => import('@/views/NotFound.vue')),
        meta: {title: 'Page not found'}
      },
      {
        path: '/error',
        component: () => defineAsyncComponent(() => import('@/views/Error.vue')),
        meta: {title: 'Error'}
      }
    ],
    component: () => defineAsyncComponent(() => import('@/layouts/default/Default.vue')),
    path: '/',
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
