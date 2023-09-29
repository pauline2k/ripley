<template>
  <div v-if="!isLoading" class="mx-10 my-5">
    <v-container fluid>
      <v-row no-gutters>
        <v-col>
          <Header1 text="Create a Site" />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <v-divider class="mb-4" />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="2">
          <div class="bg-blue-lighten-5 float-right pa-2">
            <v-icon icon="mdi-school" size="120" />
          </div>
        </v-col>
        <v-col cols="10">
          <div class="pl-4">
            <h2>Course Sites</h2>
            <div class="pb-4 pt-2">
              <div v-if="canCreateCourseSite">
                Set up course sites to communicate with and manage the work of students enrolled in your classes.
              </div>
              <div v-if="!canCreateCourseSite">
                To create a course site, you will need to be the official instructor of record for a course.
                If you have not been assigned as the official instructor of record for the course,
                please contact your department scheduler.
                You will be able to create a course site the day after you have been officially assigned to teach the course.
              </div>
            </div>
            <div v-if="canCreateCourseSite">
              <v-btn
                id="create-course-site"
                color="primary"
                @click="goCreateCourseSite"
              >
                Create a Course Site
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <v-divider class="my-4" />
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="2">
          <div class="bg-blue-lighten-5 float-right pa-2">
            <v-icon icon="mdi-chart-bar-stacked" size="120" />
          </div>
        </v-col>
        <v-col cols="10">
          <div class="pl-4">
            <h2>Project Sites</h2>
            <div class="pb-4 pr-2 pt-2">
              <div>
                Share files and collaborate. Project sites are best suited for instructors and GSIs who already use bCourses.
                Project sites cannot access all bCourses features and are not intended for lecture, lab, or discussion sections.
                Learn more about
                <OutboundLink id="bcourses-project-sites-service-page" href="https://rtl.berkeley.edu/services-programs/bcourses-project-sites">Project Sites</OutboundLink> and
                <OutboundLink id="berkeley-collaboration-services-information" href="https://bconnected.berkeley.edu/collaboration-services">other collaboration tools at UC Berkeley</OutboundLink>.
              </div>
            </div>
            <div v-if="canCreateProjectSite">
              <v-btn
                id="create-project-site"
                color="primary"
                @click="goCreateProjectSite"
              >
                Create a Project Site
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <v-divider class="my-4" />
        </v-col>
      </v-row>
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
    canCreateCourseSite: undefined,
    canCreateProjectSite: undefined,
    createProjectSiteButtonFocus: undefined
  }),
  created() {
    getSiteCreationAuthorizations().then(data => {
      this.canCreateCourseSite = data.authorizations.canCreateCourseSite
      this.canCreateProjectSite = data.authorizations.canCreateProjectSite
      this.$ready()
    })
  },
  methods: {
    goCreateCourseSite() {
      this.$router.push({path: '/create_course_site'})
    },
    goCreateProjectSite() {
      this.$router.push({path: '/create_project_site'})
    }
  }
}
</script>
