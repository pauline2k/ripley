<template>
  <div v-if="!isLoading" class="canvas-application mx-10 my-5">
    <h1>Create a Site</h1>
    <v-container class="ml-4" fluid>
      <v-row class="ml-8" no-gutters>
        <v-col sm="2">
          <div class="bg-blue-grey-lighten-5 float-right pa-2 mr-8">
            <v-icon icon="mdi-school" size="120" />
          </div>
        </v-col>
        <v-col sm="10">
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
          <div>
            <v-btn
              id="create-course-site"
              color="primary"
              :disabled="!canCreateCourseSite"
              :href="linkToCreateCourseSite"
              @click="goCreateCourseSite"
              @keypress="goCreateCourseSite"
            >
              Create a Course Site
            </v-btn>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <v-divider class="my-4" />
        </v-col>
      </v-row>
      <v-row class="ml-8" no-gutters>
        <v-col sm="2">
          <div class="bg-blue-grey-lighten-5 float-right pa-2 mr-8">
            <v-icon icon="mdi-chart-bar-stacked" size="120" />
          </div>
        </v-col>
        <v-col sm="10">
          <h2>Project Sites</h2>
          <div class="pb-4 pt-2">
            <div>
              Share files and collaborate with your team. Projects are best suited for instructors and GSIs who already
              use bCourses.
            </div>
            <div class="pt-2">
              Project sites do not have access to all bCourses features, and are not intended for
              lecture, lab, or discussion sections.
              Learn more about <OutboundLink id="bcourses-project-sites-service-page" href="https://rtl.berkeley.edu/services-programs/bcourses-project-sites">Project Sites</OutboundLink>, and <OutboundLink id="berkeley-collaboration-services-information" href="https://bconnected.berkeley.edu/collaboration-services">other collaboration tools available at UC Berkeley.</OutboundLink>
            </div>
          </div>
          <div>
            <v-btn
              id="create-project-site"
              color="primary"
              :disabled="!canCreateProjectSite"
              :href="linkToCreateProjectSite"
              @click="goCreateProjectSite"
              @keypress="goCreateProjectSite"
            >
              Create a Project Site
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import {getSiteCreationAuthorizations} from '@/api/canvas-utility'

export default {
  name: 'SiteCreation',
  mixins: [Context],
  components: {OutboundLink},
  data: () => ({
    canCreateCourseSite: undefined,
    canCreateProjectSite: undefined,
    createProjectSiteButtonFocus: undefined,
    linkToCreateCourseSite: undefined,
    linkToCreateProjectSite: undefined
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
      const path = this.$isInIframe ? '/lti/create_course_site' : '/create_course_site'
      this.$router.push({path})
    },
    goCreateProjectSite() {
      const path = this.$isInIframe ? '/lti/create_project_site' : '/create_project_site'
      this.$router.push({path})
    }
  }
}
</script>
