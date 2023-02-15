import _ from 'lodash'
import auth from '@/auth'
import BaseLTI from '@/layouts/lti/BaseLTI.vue'
import BaseStandalone from '@/layouts/standalone/BaseStandalone.vue'
import CourseAddUser from '@/views/CourseAddUser.vue'
import CourseGradeExport from '@/views/CourseGradeExport.vue'
import CourseManageOfficialSections from '@/views/CourseManageOfficialSections.vue'
import CreateCourseSite from '@/views/CreateCourseSite.vue'
import CreateProjectSite from '@/views/CreateProjectSite.vue'
import Jobs from '@/views/Jobs.vue'
import Login from '@/views/Login.vue'
import NotFound from '@/views/NotFound.vue'
import Roster from '@/views/Roster.vue'
import SiteCreation from '@/views/SiteCreation.vue'
import SiteMailingList from '@/views/SiteMailingList.vue'
import SiteMailingLists from '@/views/SiteMailingLists.vue'
import UserProvision from '@/views/UserProvision.vue'
import Welcome from '@/views/Welcome.vue'
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
    component: BaseStandalone,
    path: '/',
  },
  {
    component: BaseStandalone,
    path: '/canvas',
    children: [
      {
        component: CourseAddUser,
        path: '/canvas/course_add_user/:id',
        meta: {
          title: 'Find a User to Add'
        }
      },
      {
        component: CourseGradeExport,
        path: '/canvas/course_grade_export/:id',
        meta: {
          title: 'E-Grade Export'
        }
      },
      {
        component: CourseManageOfficialSections,
        path: '/canvas/course_manage_official_sections/:id',
        meta: {
          title: 'Official Sections'
        }
      },
      {
        component: Roster,
        path: '/canvas/rosters/:id',
        meta: {
          title: 'bCourses Roster Photos'
        }
      },
      {
        component: SiteCreation,
        path: '/canvas/site_creation',
        meta: {
          title: 'bCourses Site Creation'
        }
      },
      {
        component: CreateCourseSite,
        path: '/canvas/create_course_site',
        meta: {
          title: 'Create a Course Site'
        }
      },
      {
        component: CreateProjectSite,
        path: '/canvas/create_project_site',
        meta: {
          title: 'Create a Project Site'
        }
      },
      {
        component: SiteMailingList,
        path: '/canvas/site_mailing_list/:id',
        meta: {
          title: 'bCourses Mailing List'
        }
      },
      {
        component: SiteMailingLists,
        path: '/canvas/site_mailing_lists',
        meta: {
          title: 'bCourses Site Mailing Lists'
        }
      },
      {
        component: UserProvision,
        path: '/canvas/user_provision',
        meta: {
          title: 'bCourses User Provision'
        }
      }
    ]
  },
  {
    component: BaseLTI,
    path: '/canvas/embedded',
    children: [
      {
        component: CourseAddUser,
        path: '/canvas/embedded/course_add_user'
      },
      {
        component: CourseGradeExport,
        path: '/canvas/embedded/course_grade_export'
      },
      {
        component: CourseManageOfficialSections,
        path: '/canvas/embedded/course_manage_official_sections'
      },
      {
        component: CreateCourseSite,
        path: '/canvas/embedded/create_course_site'
      },
      {
        component: CreateProjectSite,
        path: '/canvas/embedded/create_project_site'
      },
      {
        component: Roster,
        path: '/canvas/embedded/rosters'
      },
      {
        component: SiteCreation,
        path: '/canvas/embedded/site_creation'
      },
      {
        component: SiteMailingList,
        path: '/canvas/embedded/site_mailing_list'
      },
      {
        component: SiteMailingLists,
        path: '/canvas/embedded/site_mailing_lists'
      },
      {
        component: UserProvision,
        path: '/canvas/embedded/user_provision'
      }
    ]
  },
  {
    beforeEnter: auth.requiresAdmin,
    children: [
      {
        component: Welcome,
        name: 'Welcome',
        path: '/welcome',
      },
      {
        path: '/jobs',
        component: Jobs,
        meta: {title: 'MU-TH-UR 6000'}
      }
    ],
    component: BaseStandalone,
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
        component: NotFound,
        meta: {title: 'Page not found'}
      },
      {
        path: '/error',
        component: Error,
        meta: {title: 'Error'}
      }
    ],
    component: BaseStandalone,
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
