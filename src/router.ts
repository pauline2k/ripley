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
import Profile from '@/views/Profile.vue'
import Roster from '@/views/Roster.vue'
import SiteCreation from '@/views/SiteCreation.vue'
import SiteMailingList from '@/views/SiteMailingList.vue'
import SiteMailingLists from '@/views/SiteMailingLists.vue'
import UserProvision from '@/views/UserProvision.vue'
import Welcome from '@/views/Welcome.vue'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import {useContextStore} from '@/stores/context'


const routes:RouteRecordRaw[] = [
  {
    beforeEnter: (to: any, from: any, next: any) => {
      const currentUser = useContextStore().currentUser
      currentUser.isAuthenticated ? next({path: '/welcome'}) : next()
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
    beforeEnter: auth.requiresAuthenticated,
    component: BaseStandalone,
    path: '/',
    children: [
      {
        component: CourseAddUser,
        path: '/add_user/:id',
        meta: {
          title: 'Find a User to Add'
        }
      },
      {
        component: CourseGradeExport,
        path: '/export_grade/:id',
        meta: {
          title: 'E-Grade Export'
        }
      },
      {
        component: CourseManageOfficialSections,
        path: '/manage_official_sections/:id',
        meta: {
          title: 'Official Sections'
        }
      },
      {
        component: Profile,
        path: '/profile/:uid',
        meta: {
          title: 'Profile'
        }
      },
      {
        component: Roster,
        path: '/roster/:id',
        meta: {
          title: 'bCourses Roster Photos'
        }
      },
      {
        component: SiteCreation,
        path: '/create_site',
        meta: {
          title: 'bCourses Site Creation'
        }
      },
      {
        component: CreateCourseSite,
        path: '/create_course_site',
        meta: {
          title: 'Create a Course Site'
        }
      },
      {
        component: CreateProjectSite,
        path: '/create_project_site',
        meta: {
          title: 'Create a Project Site'
        }
      },
      {
        component: SiteMailingList,
        path: '/mailing_list/:id',
        meta: {
          title: 'bCourses Mailing List'
        }
      },
      {
        component: SiteMailingLists,
        path: '/mailing_lists',
        meta: {
          title: 'bCourses Site Mailing Lists'
        }
      },
      {
        component: UserProvision,
        path: '/provision_user',
        meta: {
          title: 'bCourses User Provision'
        }
      },
      {
        component: Welcome,
        name: 'Welcome',
        path: '/welcome',
      }
    ]
  },
  {
    beforeEnter: auth.requiresAuthenticated,
    component: BaseLTI,
    path: '/lti',
    children: [
      {
        component: CourseAddUser,
        path: '/add_user'
      },
      {
        component: CourseGradeExport,
        path: '/export_grade'
      },
      {
        component: CourseManageOfficialSections,
        path: '/manage_official_sections'
      },
      {
        component: CreateCourseSite,
        path: '/create_course_site'
      },
      {
        component: CreateProjectSite,
        path: '/create_project_site'
      },
      {
        component: Roster,
        path: '/roster'
      },
      {
        component: SiteCreation,
        path: '/create_site'
      },
      {
        component: SiteMailingList,
        path: '/mailing_list'
      },
      {
        component: SiteMailingLists,
        path: '/mailing_lists'
      },
      {
        component: UserProvision,
        path: '/provision_user'
      }
    ]
  },
  {
    beforeEnter: auth.requiresAdmin,
    children: [
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
    beforeEnter: () => useContextStore().setApplicationState(404),
    component: NotFound,
    path: '/:pathMatch(.*)'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(() => {
  useContextStore().resetApplicationState()
})

router.afterEach((to: any) => {
  const title = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome'
  document.title = `${title} | UC Berkeley`
})

export default router
