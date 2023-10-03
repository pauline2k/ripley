<template>
  <div v-if="!isLoading" class="mx-10 my-5">
    <v-container fluid>
      <v-row no-gutters>
        <v-col class="mx-16">
          <Header1 text="Manage Sites" />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col class="mx-16">
          <v-divider class="mb-4" />
        </v-col>
      </v-row>
      <template v-for="option in options" :key="option.path">
        <v-row no-gutters>
          <v-col cols="2">
            <div class="bg-blue-lighten-5 float-right pa-2">
              <v-icon :icon="option.icon" size="120" />
            </div>
          </v-col>
          <v-col cols="10">
            <div class="pl-4 pr-16">
              <h2>{{ option.header }}</h2>
              <div class="pb-4 pr-2 pt-2">
                <div v-if="option.id === 'create-course-site'">
                  <div v-if="option.isAvailable">
                    Set up course sites to communicate with and manage the work of students enrolled in your classes.
                  </div>
                  <div v-if="!option.isAvailable">
                    To create a course site, you will need to be the official instructor of record for a course.
                    If you have not been assigned as the official instructor of record for the course,
                    please contact your department scheduler.
                    You will be able to create a course site the day after you have been officially assigned to teach the course.
                  </div>
                </div>
                <div v-if="option.id === 'create-project-site'">
                  Share files and collaborate. Project sites are best suited for instructors and GSIs who already use bCourses.
                  Project sites cannot access all bCourses features and are not intended for lecture, lab, or discussion sections.
                  Learn more about
                  <OutboundLink id="bcourses-project-sites-service-page" href="https://rtl.berkeley.edu/services-programs/bcourses-project-sites">Project Sites</OutboundLink> and
                  <OutboundLink id="berkeley-collaboration-services-information" href="https://bconnected.berkeley.edu/collaboration-services">other collaboration tools at UC Berkeley</OutboundLink>.
                </div>
                <div v-if="option.id === 'manage-site-sections'">
                  Foo.
                </div>
              </div>
              <div v-if="option.isAvailable">
                <v-btn
                  :id="option.id"
                  color="primary"
                  @click="() => $router.push({path: option.path})"
                >
                  {{ option.label }}
                </v-btn>
              </div>
            </div>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col class="mx-16">
            <v-divider class="my-4" />
          </v-col>
        </v-row>
      </template>
    </v-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import {getSiteCreationAuthorizations} from '@/api/canvas-utility'

export default {
  name: 'SiteCreation',
  mixins: [Context],
  components: {Header1, OutboundLink},
  data: () => ({
    createProjectSiteButtonFocus: undefined,
    options: undefined
  }),
  created() {
    getSiteCreationAuthorizations().then(data => {
      const canCreateCourseSite = data.authorizations.canCreateCourseSite
      const canCreateProjectSite = data.authorizations.canCreateProjectSite
      this.options = [
        {
          header: 'Course Sites',
          icon: 'mdi-school',
          id: 'create-course-site',
          isAvailable: canCreateCourseSite,
          label: 'Create a Course Site',
          path: '/create_course_site'
        },
        {
          header: 'Project Sites',
          icon: 'mdi-chart-bar-stacked',
          id: 'create-project-site',
          isAvailable: canCreateProjectSite,
          label: 'Create a Project Site',
          path: '/create_project_site'
        },
        {
          header: 'Manage Site Sections',
          icon: 'mdi-view-dashboard-edit',
          id: 'manage-site-sections',
          isAvailable: canCreateCourseSite,
          label: 'Manage Sections',
          path: '/manage_sites'
        }
      ]
      this.$ready()
    })
  }
}
</script>
