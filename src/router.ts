import _ from 'lodash'
import Default from '@/layouts/default/Default.vue'
import Jobs from '@/views/Jobs.vue'
import Login from '@/views/Login.vue'
import NotFound from '@/views/NotFound.vue'
import Welcome from '@/views/Welcome.vue'
import auth from '@/auth'
import {app} from '@/main'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'

const routes:RouteRecordRaw[] = [
  {
    beforeEnter: (to: any, from: any, next: any) => {
      const currentUser = app.config.globalProperties.$currentUser
      currentUser.isAuthenticated ? (currentUser.isAdmin ? next({path: '/jobs'}) : next({path: '/welcome'})) : next()
    },
    children: [
      {
        component: Login,
        name: 'Login',
        path: '',
      }
    ],
    component: Default,
    path: '/',
  },
    {
    beforeEnter: auth.requiresAdmin,
    children: [
      {
        component: () => Welcome,
        name: 'Welcome',
        path: '/welcome',
      },
      {
        path: '/jobs',
        component: () => Jobs,
        meta: {title: 'MU-TH-UR 6000'}
      }
    ],
    component: Default,
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
        component: () => NotFound,
        meta: {title: 'Page not found'}
      },
      {
        path: '/error',
        component: () => Error,
        meta: {title: 'Error'}
      }
    ],
    component: Default,
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
