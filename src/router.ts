import _ from 'lodash'
import auth from "@/auth"
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'

const routes:RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/toolbox'
  },
  {
    beforeEnter: (to: any, from: any, next: any) => {
      const currentUser = {isLoggedIn: true} // TODO: pull from globalProperties or use Vue 3 'provide'
      if (currentUser && currentUser.isLoggedIn) {
        if (_.trim(to.query.redirect)) {
          next(to.query.redirect)
        } else {
          next({path: '/404'})
        }
      } else {
        next()
      }
    },
    path: '/login',
    component: () => import('@/views/BaseView.vue'),
    children: [
      {
        component: () => import('@/views/Login.vue'),
        path: '/login',
        meta: {
          title: 'Welcome'
        }
      }
    ]
  },
  {
    path: '/',
    beforeEnter: auth.requiresAuthenticated,
    component: () => import('@/views/BaseView.vue'),
    children: [
      {
        component: () => import('@/views/Toolbox.vue'),
        name: 'toolbox',
        path: '/toolbox',
        meta: {
          title: 'Toolbox'
        }
      },
      // {
      //   component: StandaloneLti,
      //   path: '/canvas',
      //   children: [
      //     {
      //       component: CourseAddUser,
      //       path: '/canvas/course_add_user/:id',
      //       meta: {
      //         title: 'Find a User to Add'
      //       }
      //     },
      //     {
      //       component: CourseCaptures,
      //       path: '/canvas/course_mediacasts/:id',
      //       meta: {
      //         title: 'Course Captures'
      //       }
      //     },
      //     {
      //       component: CourseGradeExport,
      //       path: '/canvas/course_grade_export/:id',
      //       meta: {
      //         title: 'E-Grade Export'
      //       }
      //     },
      //     {
      //       component: CourseManageOfficialSections,
      //       path: '/canvas/course_manage_official_sections/:id',
      //       meta: {
      //         title: 'Official Sections'
      //       }
      //     },
      //     {
      //       component: Roster,
      //       path: '/canvas/rosters/:id',
      //       meta: {
      //         title: 'bCourses Roster Photos'
      //       }
      //     },
      //     {
      //       component: SiteCreation,
      //       path: '/canvas/site_creation',
      //       meta: {
      //         title: 'bCourses Site Creation'
      //       }
      //     },
      //     {
      //       component: CreateCourseSite,
      //       path: '/canvas/create_course_site',
      //       meta: {
      //         title: 'Create a Course Site'
      //       }
      //     },
      //     {
      //       component: CreateProjectSite,
      //       path: '/canvas/create_project_site',
      //       meta: {
      //         title: 'Create a Project Site'
      //       }
      //     },
      //     {
      //       component: SiteMailingList,
      //       path: '/canvas/site_mailing_list/:id',
      //       meta: {
      //         title: 'bCourses Mailing List'
      //       }
      //     },
      //     {
      //       component: SiteMailingLists,
      //       path: '/canvas/site_mailing_lists',
      //       meta: {
      //         title: 'bCourses Site Mailing Lists'
      //       }
      //     },
      //     {
      //       component: UserProvision,
      //       path: '/canvas/user_provision',
      //       meta: {
      //         title: 'bCourses User Provision'
      //       }
      //     }
      //   ]
      // },
      // {
      //   component: EmbeddedLti,
      //   path: '/canvas/embedded',
      //   children: [
      //     {
      //       component: CourseAddUser,
      //       path: '/canvas/embedded/course_add_user'
      //     },
      //     {
      //       component: CourseCaptures,
      //       path: '/canvas/embedded/course_mediacasts'
      //     },
      //     {
      //       component: CourseGradeExport,
      //       path: '/canvas/embedded/course_grade_export'
      //     },
      //     {
      //       component: CourseManageOfficialSections,
      //       path: '/canvas/embedded/course_manage_official_sections'
      //     },
      //     {
      //       component: CreateCourseSite,
      //       path: '/canvas/embedded/create_course_site'
      //     },
      //     {
      //       component: CreateProjectSite,
      //       path: '/canvas/embedded/create_project_site'
      //     },
      //     {
      //       component: Roster,
      //       path: '/canvas/embedded/rosters'
      //     },
      //     {
      //       component: SiteCreation,
      //       path: '/canvas/embedded/site_creation'
      //     },
      //     {
      //       component: SiteMailingList,
      //       path: '/canvas/embedded/site_mailing_list'
      //     },
      //     {
      //       component: SiteMailingLists,
      //       path: '/canvas/embedded/site_mailing_lists'
      //     },
      //     {
      //       component: UserProvision,
      //       path: '/canvas/embedded/user_provision'
      //     }
      //   ]
      // }
    ]
  },
  // {
  //   path: '/',
  //   component: BaseView,
  //   children: [
  //     {
  //       beforeEnter: (to: any, from: any, next: any) => {
  //         to.params.m = to.redirectedFrom
  //         next()
  //       },
  //       path: '/404',
  //       component: NotFound,
  //       meta: {
  //         title: 'Page not found'
  //       }
  //     },
  //     {
  //       path: '/error',
  //       component: Error,
  //       meta: {
  //         title: 'Error'
  //       }
  //     }
  //   ]
  // },
  // {
  //   path: '*',
  //   redirect: '/404'
  // }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

router.afterEach((to: any) => {
  const title = _.get(to, 'meta.title') || _.capitalize(to.name) || 'Welcome'
  document.title = `${title} | Junction`
})

export default router
