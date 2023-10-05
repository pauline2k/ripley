<template>
  <div v-if="!isLoading" class="pt-3 px-16">
    <Header1 class="mb-2" text="Create or Update bCourses Sites" />
    <v-radio-group
      v-model="selection"
      class="d-flex"
      hide-details
    >
      <ul>
        <li
          v-for="option in options"
          :key="option.id"
          class="my-2 px-3 py-1"
          :class="{
            'highlight-when-hover': !selection,
            'highlight-when-selected': selection === option
          }"
        >
          <div class="d-flex">
            <div class="radio-button-container">
              <v-radio
                :id="option.id"
                :class="{'text-grey': !option.isAvailable}"
                :disabled="!option.isAvailable"
                :value="option"
              />
            </div>
            <div class="list-item-content">
              <label class="w-100" :for="option.id">
                <h2>{{ option.header }}</h2>
              </label>
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
                <OutboundLink id="bcourses-project-sites-service-page" href="https://rtl.berkeley.edu/services-programs/bcourses-project-sites">Project Sites</OutboundLink>
                and
                <OutboundLink id="berkeley-collaboration-services-information" href="https://bconnected.berkeley.edu/collaboration-services">other collaboration tools at UC Berkeley</OutboundLink>.
              </div>
              <div v-if="option.id === 'manage-official-sections'">
                <div class="pt-2">
                  <div v-if="size(coursesByTerm)">
                    Add or remove official section rosters in already-created course sites.
                    <div class="pl-3 py-2">
                      <div v-for="(courses, termId) in coursesByTerm" :key="termId">
                        <div class="text-subtitle-1">{{ getTermName(termId) }}</div>
                        <select
                          id="course-sections"
                          v-model="canvasSiteId"
                          :disabled="!selection || selection.id !== 'manage-official-sections'"
                        >
                          <option :value="null">Choose...</option>
                          <option
                            v-for="course in courses"
                            :key="course.canvasSiteId"
                            :value="course.canvasSiteId"
                          >
                            {{ course.courseCode }} &mdash; {{ course.name }}
                          </option>
                        </select>
                      </div>
                    </div>
                  </div>
                  <div v-if="!size(coursesByTerm)">
                    <span class="text-red">
                      Sorry, this option is not available.
                      You are an instructor of neither current nor upcoming classes.
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </li>
      </ul>
    </v-radio-group>
    <div class="w-100">
      <v-btn
        id="go-next-btn"
        class="float-right"
        color="primary"
        :disabled="isButtonDisabled"
        size="large"
        @click="goNext"
      >
        Next
      </v-btn>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import {each, size} from 'lodash'
import {getSiteCreationAuthorizations} from '@/api/canvas-utility'
import {getTermName} from '@/utils'
import {myCurrentCanvasCourses} from '@/api/canvas-site'

export default {
  name: 'ManageSites',
  mixins: [Context],
  components: {Header1, OutboundLink},
  data: () => ({
    canvasSiteId: null,
    coursesByTerm: undefined,
    options: undefined,
    selection: undefined
  }),
  computed: {
    isButtonDisabled() {
      return !this.selection || (this.selection.id === 'manage-official-sections' && !this.canvasSiteId)
    }
  },
  watch: {
    selection() {
      this.canvasSiteId = null
    }
  },
  created() {
    this.coursesByTerm = {}
    myCurrentCanvasCourses().then(data => {
      each(data, (courses, term) => {
        if (courses.length) {
          this.coursesByTerm[term] = courses
        }
      })
      getSiteCreationAuthorizations().then(data => {
        const canCreateCourseSite = data.authorizations.canCreateCourseSite
        const canCreateProjectSite = data.authorizations.canCreateProjectSite
        this.options = [
          {
            header: 'Create a course site',
            icon: 'mdi-school',
            id: 'create-course-site',
            isAvailable: canCreateCourseSite,
            label: 'Create a Course Site',
            path: '/create_course_site'
          },
          {
            header: 'Create a project site',
            icon: 'mdi-chart-bar-stacked',
            id: 'create-project-site',
            isAvailable: canCreateProjectSite,
            label: 'Create a Project Site',
            path: '/create_project_site'
          },
          {
            header: 'Manage official sections of an existing site',
            icon: 'mdi-view-dashboard-edit',
            id: 'manage-official-sections',
            isAvailable: canCreateCourseSite && size(this.coursesByTerm),
            label: 'Manage Official Sections',
            path: '/manage_sites'
          }
        ]
        this.$ready()
      })
    })
  },
  methods: {
    each,
    getTermName,
    goNext() {
      if (!this.isButtonDisabled) {
        const path = this.selection.id === 'manage-official-sections' ? `/manage_official_sections/${this.canvasSiteId}` : this.selection.path
        this.$router.push({path})
      }
    },
    size
  }
}
</script>

<style scoped>
li {
  border: 1px solid #fff;
}
ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
}
.highlight-when-hover:hover {
  background-color: rgb(233, 239, 243);
}
.highlight-when-selected {
  background-color: rgb(233, 239, 243);
  border: 1px solid #d0d0d0 !important;
}
.list-item-content {
  color: black;
  padding: 6px 0;
}
.radio-button-container {
  padding: 2px 8px 0 0;
}
</style>
