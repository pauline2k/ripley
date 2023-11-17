<template>
  <div v-if="!isLoading" class="pt-3 px-16">
    <Header1 class="mb-1" text="Create or Update bCourses Sites" />
    <div v-if="!size(coursesByTerm) && !currentUser.isAdmin" class="font-italic font-weight-medium text-red">
      Sorry, we found neither {{ config.terms.current.name }} nor {{ config.terms.next.name }}
      courses in which you are listed as an instructor.
    </div>
    <v-radio-group
      v-model="selection"
      class="d-flex"
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
                :disabled="!option.isAvailable || isProcessing"
                :value="option"
              />
            </div>
            <div class="list-item-content">
              <label class="w-100" :for="option.id">
                <h2 :class="{'text-grey': !option.isAvailable}">{{ option.header }}</h2>
                <span class="sr-only">.</span>
              </label>
              <div v-if="option.id === 'create-course-site'">
                <div v-if="option.isAvailable" @click="() => selection = option">
                  Set up course sites to communicate with and manage the work of students enrolled in your classes.
                </div>
                <div v-if="!option.isAvailable" class="text-grey">
                  To create a course site, you will need to be the official instructor of record for a course.
                  If you have not been assigned as the official instructor of record for the course,
                  please contact your department scheduler.
                  You will be able to create a course site the day after you have been officially assigned to teach the course.
                </div>
              </div>
              <div
                v-if="option.id === 'create-project-site'"
                :class="{'text-grey': !option.isAvailable}"
                @click="() => selection = option"
              >
                Share files and collaborate. Project sites are best suited for instructors and <span :aria-hidden="true">GSIs</span><span class="sr-only">G S I's</span> who already use bCourses.
                Project sites cannot access all bCourses features and are not intended for lecture, lab, or discussion sections.
                Learn more about
                <OutboundLink id="bcourses-project-sites-service-page" href="https://rtl.berkeley.edu/services-programs/bcourses-project-sites">Project Sites</OutboundLink>
                and
                <OutboundLink id="berkeley-collaboration-services-information" href="https://bconnected.berkeley.edu/collaboration-services">other collaboration tools at UC Berkeley</OutboundLink>.
              </div>
              <div v-if="option.id === 'manage-official-sections'" class="pt-2" @click="() => selection = option">
                <div v-if="size(coursesByTerm)" :class="{'text-grey': !option.isAvailable}">
                  <div>
                    Add or remove official section rosters in already-created course sites.
                  </div>
                  <div v-if="option.isAvailable" class="pl-3 py-2">
                    <select
                      id="course-sections"
                      v-model="canvasSiteId"
                      aria-label="All your courses"
                      :disabled="isManageOfficialSectionsDisabled"
                    >
                      <option :value="null">Choose a course</option>
                      <optgroup
                        v-for="(courses, termId) in coursesByTerm"
                        :key="termId"
                        class="text-subtitle-1"
                        :label="getTermName(termId)"
                      >
                        <option
                          v-for="course in labelCourses(courses)"
                          :id="`canvas-site-${course.canvasSiteId}`"
                          :key="course.canvasSiteId"
                          :aria-label="`${getTermName(termId)} group: ${course.courseCode} ${course.name}`"
                          :value="course.canvasSiteId"
                          v-html="course.label"
                        />
                      </optgroup>
                    </select>
                  </div>
                </div>
                <div v-if="currentUser.isAdmin" class="mt-2 pl-3">
                  <label class="sr-only" for="canvas-site-id-input">Canvas Site I D:</label>
                  <v-text-field
                    id="canvas-site-id-input"
                    v-model="canvasSiteId"
                    density="compact"
                    :disabled="isManageOfficialSectionsDisabled"
                    :error="!!trim(canvasSiteId) && !isCanvasSiteIdValid"
                    hide-details
                    label="Canvas Site ID"
                    maxlength="9"
                    style="width: 148px"
                    variant="outlined"
                    @keydown.enter="goNext"
                  />
                </div>
                <div
                  v-if="error"
                  aria-live="polite"
                  class="font-italic font-weight-medium text-red"
                  role="alert"
                >
                  {{ error }}
                </div>
              </div>
            </div>
          </div>
        </li>
      </ul>
    </v-radio-group>
    <div class="pr-8">
      <v-btn
        id="go-next-btn"
        class="float-right mt-1"
        color="primary"
        :disabled="isButtonDisabled || isProcessing"
        size="large"
        @click="goNext"
      >
        <span v-if="isProcessing">
          <SpinnerWithinButton /> Next
        </span>
        <span v-if="!isProcessing">Next</span>
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton'
import {getTermName} from '@/utils'
</script>

<script>
import Context from '@/mixins/Context'
import {each, get, map, size, trim, uniq} from 'lodash'
import {getSiteCreationAuthorizations} from '@/api/canvas-utility'
import {isValidCanvasSiteId, putFocusNextTick} from '@/utils'
import {getCanvasSite, getManageOfficialSections} from '@/api/canvas-site'

export default {
  name: 'ManageSites',
  mixins: [Context],
  data: () => ({
    canvasSiteId: null,
    coursesByTerm: undefined,
    error: undefined,
    isProcessing: false,
    options: undefined,
    selection: undefined
  }),
  computed: {
    isButtonDisabled() {
      return !this.selection || (this.selection.id === 'manage-official-sections' && !this.isCanvasSiteIdValid)
    },
    isCanvasSiteIdValid() {
      return isValidCanvasSiteId(this.canvasSiteId)
    },
    isManageOfficialSectionsDisabled() {
      return !this.selection || this.selection.id !== 'manage-official-sections' || this.isProcessing
    }
  },
  watch: {
    selection() {
      this.canvasSiteId = null
      if (get(this.selection, 'id') === 'manage-official-sections') {
        putFocusNextTick('canvas-site-id-input')
      }
    }
  },
  created() {
    this.coursesByTerm = {}
    getManageOfficialSections().then(data => {
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
            id: 'create-course-site',
            isAvailable: canCreateCourseSite,
            label: 'Create a Course Site',
            path: '/create_course_site'
          },
          {
            header: 'Create a project site',
            id: 'create-project-site',
            isAvailable: canCreateProjectSite,
            label: 'Create a Project Site',
            path: '/create_project_site'
          },
          {
            header: 'Manage official sections of an existing site',
            id: 'manage-official-sections',
            isAvailable: this.currentUser.isAdmin || size(this.coursesByTerm),
            label: 'Manage Official Sections',
            path: '/manage_sites'
          }
        ]
        if (!canCreateCourseSite && !canCreateProjectSite) {
          this.selection = this.options[2]
        }
        this.$ready()
      })
    })
  },
  methods: {
    each,
    goNext() {
      if (!this.isButtonDisabled) {
        this.isProcessing = true
        if (this.selection.id === 'manage-official-sections') {
          getCanvasSite(this.canvasSiteId).then(
            () => this.$router.push({path: `/official_sections/${this.canvasSiteId}`}),
            error => this.error = error
          ).finally(() => this.isProcessing = false)
        } else {
          this.$router.push({path: this.selection.path})
          this.isProcessing = false
        }
      }
    },
    labelCourses(courses) {
      const getLabel = (course, enhance) => {
        const prefix = enhance ? `${course.canvasSiteId}: ` : ''
        return `${prefix}${course.courseCode} &mdash; ${course.name}`
      }
      const enhance = uniq(map(courses, c => getLabel(c))).length !== courses.length
      return map(courses, c => ({...c, label: getLabel(c, enhance)}))
    },
    size,
    trim
  }
}
</script>

<style scoped lang="scss">
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
  min-width: 100%;
  padding: 6px 48px 12px 0;
}
.radio-button-container {
  padding: 2px 8px 0 0;
}
</style>
