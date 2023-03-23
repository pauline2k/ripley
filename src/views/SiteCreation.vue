<template>
  <div v-if="!isLoading" class="page-site-creation">
    <h1 class="page-site-creation-primary-header">Create a Site</h1>
    <v-container>
      <v-row>
        <v-col sm="3">
          <div class="pl-4">
            <div class="page-site-creation-feature-icon-box">
              <v-icon
                class="page-site-creation-feature-icon"
                :class="{'page-site-creation-feature-icon-disabled': !canCreateCourseSite}"
                icon="mdi-graduation-cap"
              />
            </div>
          </div>
        </v-col>
        <v-col sm="9">
          <div class="page-site-creation-feature-details mr-5 pr-5">
            <h2 class="page-site-creation-h2">Course Sites</h2>
            <div v-if="canCreateCourseSite" class="page-site-creation-feature-description">
              Set up course sites to communicate with and manage the work of students enrolled in your classes.
            </div>
            <div v-if="!canCreateCourseSite" class="page-site-creation-feature-description">
              To create a course site, you will need to be the official instructor of record for a course.
              If you have not been assigned as the official instructor of record for the course,
              please contact your department scheduler.
              You will be able to create a course site the day after you have been officially assigned to teach the course.
            </div>
            <div class="page-site-creation-feature-button-wrapper">
              <a
                id="create-course-site"
                :disabled="!canCreateCourseSite"
                :href="linkToCreateCourseSite"
                class="canvas-button canvas-button-primary"
                :tabindex="canCreateCourseSite ? 0 : -1"
                @click="goCreateCourseSite"
                @keypress="goCreateCourseSite"
              >
                Create a Course Site
              </a>
            </div>
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col>
          <div class="page-site-creation-features-divider"></div>
        </v-col>
      </v-row>

      <v-row>
        <v-col sm="3">
          <div class="pl-4">
            <div class="page-site-creation-feature-icon-box">
              <v-icon icon="mdi-cubes" class="page-site-creation-feature-icon" />
            </div>
          </div>
        </v-col>
        <v-col sm="9">
          <div class="page-site-creation-feature-details mr-5 pr-5">
            <h2 class="page-site-creation-h2">Project Sites</h2>
            <div class="page-site-creation-feature-description">
              Share files and collaborate with your team. Projects are best suited for instructors and GSIs who already
              use bCourses.
            </div>
            <div class="page-site-creation-feature-description pt-3">
              Project sites do not have access to all bCourses features, and are not intended for
              lecture, lab, or discussion sections.
              Learn more about <OutboundLink id="bcourses-project-sites-service-page" href="https://rtl.berkeley.edu/services-programs/bcourses-project-sites">Project Sites</OutboundLink>, and <OutboundLink id="berkeley-collaboration-services-information" href="https://bconnected.berkeley.edu/collaboration-services">other collaboration tools available at UC Berkeley.</OutboundLink>
            </div>
            <div class="page-site-creation-feature-button-wrapper">
              <a
                id="create-project-site"
                :disabled="!canCreateProjectSite"
                :tabindex="canCreateProjectSite ? 0 : -1"
                :href="linkToCreateProjectSite"
                class="canvas-button canvas-button-primary"
                @click="goCreateProjectSite"
                @keypress="goCreateProjectSite"
              >
                Create a Project Site
              </a>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import IFrameMixin from '@/mixins/IFrameMixin'
import OutboundLink from '@/components/utils/OutboundLink'
import {getSiteCreationAuthorizations} from '@/api/canvas-utility'

export default {
  name: 'SiteCreation',
  mixins: [Context, IFrameMixin],
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
      const path = this.isInIframe ? '/lti/create_course_site' : '/create_course_site'
      this.$router.push({path})
    },
    goCreateProjectSite() {
      const path = this.isInIframe ? '/lti/create_project_site' : '/create_project_site'
      this.$router.push({path})
    }
  }
}
</script>

<style scoped lang="scss">
.page-site-creation {
  background: $color-white;
  padding: 10px 0;

  .page-site-creation-feature-button-wrapper {
    margin-top: 25px;
  }

  .page-site-creation-primary-header {
    font-size: 24px;
    line-height: 30px;
    margin: 15px 25px 16px 10px;
  }

  .page-site-creation-feature-icon-box {
    background-color: $color-feature-icon-box-background;
    border: $color-feature-icon-box-border solid 1px;
    border-radius: 4px;
    display: table-cell;
    height: 150px;
    text-align: center;
    vertical-align: middle;
    width: 190px;
  }

  .page-site-creation-feature-icon {
    color: $color-headers;
    font-size: 95px;
    margin-left: auto;
    margin-right: auto;
  }

  .page-site-creation-feature-icon-disabled {
    color: $color-feature-icon-color;
  }

  .page-site-creation-feature-description {
    font-weight: 300;
    line-height: 18px;
  }

  .page-site-creation-features-container {
    margin: 0 20px;
  }

  .page-site-creation-features-divider {
    border-top: $color-button-grey-border solid 1px;
    margin: 30px 0;
  }

  .page-site-creation-h2 {
    font-size: 20px;
    margin: 0 0 13px;
  }

  @media #{$small-only} {
    .page-site-creation-feature-details {
      text-align: center;
    }
  }
}
</style>
