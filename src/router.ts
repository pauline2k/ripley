import auth from '@/auth'
const BaseLTI = () => import('./layouts/lti/BaseLTI.vue')
const BaseStandalone = () => import('./layouts/standalone/BaseStandalone.vue')
const CanvasSiteSummary = () => import('./views/CanvasSiteSummary.vue')
const CourseAddUser = () => import('./views/CourseAddUser.vue')
const CourseGradeDistribution = () => import('./views/CourseGradeDistribution.vue')
const CourseGradeExport = () => import('./views/CourseGradeExport.vue')
const CourseManageOfficialSections = () => import('./views/CourseManageOfficialSections.vue')
const CreateCourseSite = () => import('./views/CreateCourseSite.vue')
const CreateProjectSite = () => import('./views/CreateProjectSite.vue')
const Error = () => import('./views/Error.vue')
const Jobs = () => import('./views/Jobs.vue')
const Login = () => import('./views/Login.vue')
const MailingListCreate = () => import('./views/MailingListCreate.vue')
const MailingListSelectCourse = () => import('./views/MailingListSelectCourse.vue')
const MailingListUpdate = () => import('./views/MailingListUpdate.vue')
const Profile = () => import('./views/Profile.vue')
const Roster = () => import('./views/Roster.vue')
const SendWelcomeEmail = () => import('./views/SendWelcomeEmail.vue')
const SiteCreation = () => import('./views/SiteCreation.vue')
const UserProvision = () => import('./views/UserProvision.vue')
const Welcome = () => import('@/views/Welcome.vue')
import {capitalize, get} from 'lodash'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import {useContextStore} from '@/stores/context'

const BaseView = () => import(window.parent.frames.length ? '@/layouts/lti/BaseLTI.vue' : '@/layouts/standalone/BaseStandalone.vue')

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
    component: BaseView,
    path: '/',
    children: [
      {
        component: CanvasSiteSummary,
        path: '/canvas_site/:id'
      },
      {
        component: CourseAddUser,
        path: '/add_user',
        meta: {
          title: 'Find a User to Add'
        }
      },
      {
        component: CourseGradeDistribution,
        path: '/grade_distribution',
        meta: {
          title: 'Grade Distribution'
        }
      },
      {
        component: CourseGradeExport,
        path: '/export_grade',
        meta: {
          title: 'E-Grade Export'
        }
      },
      {
        component: CourseManageOfficialSections,
        path: '/manage_official_sections',
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
        path: '/roster',
        meta: {
          title: 'Roster Photos'
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
        component: MailingListCreate,
        path: '/mailing_list/create',
        meta: {
          title: 'Create Mailing List'
        }
      },
      {
        component: MailingListSelectCourse,
        path: '/mailing_list/select_course',
        meta: {
          title: 'Select Course Site'
        }
      },
      {
        component: MailingListCreate,
        path: '/mailing_list/create/:canvasSiteId',
        meta: {
          title: 'Create Mailing List'
        }
      },
      {
        component: MailingListUpdate,
        path: '/mailing_list/update',
        meta: {
          title: 'Update Mailing List'
        }
      },
      {
        component: SendWelcomeEmail,
        path: '/mailing_list/send_welcome_email',
        meta: {
          title: 'Send Welcome Email'
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
        meta: {
          isHome: true
        }
      }
    ]
  },
  {
    beforeEnter: auth.requiresAdmin,
    component: BaseStandalone,
    path: '/',
    children: [
      {
        path: '/jobs',
        component: Jobs,
        meta: {title: 'MU-TH-UR 6000'}
      }
    ]
  },
  {
    component: BaseLTI,
    path: '/',
    children: [
      {
        component: Error,
        path: '/error'
      },
      {
        component: Error,
        path: '/:pathMatch(.*)'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.afterEach((to: any) => {
  useContextStore().loadingStart()
  useContextStore().resetApplicationState()
  const title = get(to, 'meta.title') || capitalize(to.name) || 'Welcome'
  document.title = `${title} | UC Berkeley`
})

export default router
