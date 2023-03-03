<template>
  <div>
    <div v-if="!$_.size(teachingSemesters)" role="alert">
      <p>You are currently not listed as the instructor of record for any courses, so you cannot create a course site in bCourses.</p>
    </div>
    <div v-if="$_.size(teachingSemesters)">
      <div>
        <div id="page-create-course-select-semesters" class="buttonset">
          <h2 class="page-create-course-site-header page-create-course-site-header2">Term</h2>
          <span v-for="(semester, index) in teachingSemesters" :key="index">
            <input
              :id="`semester${index}`"
              type="radio"
              name="semester"
              class="visuallyhidden"
              :aria-selected="currentSemester === semester.slug"
              role="tab"
              @click="switchSemester(semester)"
            />
            <label
              :for="`semester${index}`"
              class="buttonset-button"
              role="button"
              aria-disabled="false"
              :class="{
                'buttonset-button-active': currentSemester === semester.slug,
                'buttonset-corner-left': !index,
                'buttonset-corner-right': (index === $_.size(teachingSemesters) - 1)
              }"
            >
              {{ semester.name }}
            </label>
          </span>
        </div>
      </div>
      <div class="pt-2">
        <h2 class="page-create-course-site-header page-create-course-site-header2">Official Sections</h2>
        <p>All official sections you select below will be put in ONE, single course site.</p>
        <div class="page-help-notice page-create-course-site-help-notice">
          <v-icon icon="mdi-question-circle" class="left page-help-notice-icon" />
          <div class="page-help-notice-left-margin pl-1">
            <button
              class="button-link"
              aria-haspopup="true"
              aria-controls="section-selection-help"
              :aria-expanded="`${toggle.displayHelp}`"
              @click="toggle.displayHelp = !toggle.displayHelp"
            >
              Need help deciding which official sections to select?
            </button>
            <div aria-live="polite">
              <div
                v-if="toggle.displayHelp"
                id="section-selection-help"
                class="page-help-notice-content"
              >
                <p>If you have a course with multiple sections, you will need to decide whether you want to:</p>
                <ol class="page-create-course-site-help-notice-ordered-list">
                  <li>
                    Create one, single course site which includes official sections for both your primary and secondary sections, or
                  </li>
                  <li>
                    Create multiple course sites, perhaps with one for each section, or
                  </li>
                  <li>
                    Create separate course sites based on instruction mode.
                    <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0010732#instructionmode">
                      Learn more about instruction modes in bCourses.
                    </OutboundLink>
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div>
        <form class="canvas-page-form" @submit="showConfirmation">
          <ul class="page-create-course-site-section-margin">
            <li v-for="course in coursesList" :key="course.course_id" class="sections-course-container sections-course-container-bottom-margin">
              <v-btn
                :aria-expanded="`${course.visible}`"
                class="d-flex p-0"
                variant="link"
                @click="toggleShowHide(course)"
              >
                <div class="toggle-show-hide">
                  <v-icon :icon="course.visible ? 'mdi-caret-down' : 'mdi-caret-right'" />
                  <span class="sr-only">Toggle course sections list</span>
                </div>
                <div class="btn-course-title-text pr-2 pt-1">
                  <h3 class="sections-course-title">{{ course.course_code }}<span v-if="course.title">: {{ course.title }}</span></h3>
                </div>
                <div v-if="$_.size(course.sections)" class="btn-course-title-text pt-1">
                  ({{ pluralize('section', course.sections.length, {0: 'No', 1: 'One'}) }})
                </div>
              </v-btn>
              <v-collapse :id="course.course_id" v-model="course.visible">
                <CourseSectionsTable
                  mode="createCourseForm"
                  :sections="course.sections"
                  :update-selected="updateSelected"
                />
              </v-collapse>
            </li>
          </ul>
          <div class="form-actions">
            <v-btn
              id="page-create-course-site-continue"
              class="canvas-button canvas-button-primary"
              type="button"
              :disabled="!selectedSectionsList.length"
              aria-controls="page-create-course-site-steps-container"
              aria-label="Continue to next step"
              @click="showConfirmation"
            >
              Next
            </v-btn>
            <v-btn
              id="page-create-course-site-cancel"
              aria-label="Cancel and return to Site Creation Overview"
              class="canvas-button"
              variant="link"
              @click="cancel"
            >
              Cancel
            </v-btn>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import IFrameMixin from '@/mixins/IFrameMixin'
import OutboundLink from '@/components/utils/OutboundLink'
import Utils from '@/mixins/Utils'

export default {
  name: 'SelectSectionsStep',
  mixins: [IFrameMixin, Utils],
  components: {CourseSectionsTable, OutboundLink},
  props: {
    coursesList: {
      required: true,
      type: Array
    },
    currentSemester: {
      required: true,
      type: String
    },
    selectedSectionsList: {
      required: true,
      type: Array
    },
    showConfirmation: {
      required: true,
      type: Function
    },
    switchSemester: {
      required: true,
      type: Function
    },
    teachingSemesters: {
      required: true,
      type: Array
    },
    updateSelected: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    linkToSiteOverview: undefined,
    toggle: {
      displayHelp: false
    }
  }),
  methods: {
    cancel() {
      const path = this.isInIframe ? '/lti/create_site' : '/create_site'
      this.$router.push({path})
    },
    toggleShowHide: course => course.visible = !course.visible
  }
}
</script>

<style scoped lang="scss">
.page-create-course-site-help-notice {
  margin-bottom: 20px;
  .page-create-course-site-help-notice-ordered-list {
    margin-bottom: 10px;
    margin-left: 20px;
  }

  .page-create-course-site-help-notice-paragraph {
    margin-bottom: 7px;
  }
}
.page-create-course-site-form-select-all-option {
  font-size: 12px;
  font-weight: normal;
  margin: 6px 0 4px 2px;
}
.page-create-course-site-header {
  color: $color-headers;
  font-family: $body-font-family;
  font-weight: normal;
  line-height: 40px;
  margin: 5px 0;
}
.page-create-course-site-header2 {
  font-size: 18px;
  margin: 10px 0;
}
.page-create-course-site-section-margin {
  margin: 0;
  overflow: hidden;
}
.btn-course-title-text {
  color: $color-black;
  font-weight: 300;
  text-decoration: none;
}
.toggle-show-hide {
  line-height: 1.8;
  width: 20px;
}
</style>
