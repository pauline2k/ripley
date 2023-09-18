<template>
  <div class="page-create-course-site-select-sections">
    <div v-if="!size(teachingTerms)" role="alert">
      <p>You are currently not listed as the instructor of record for any courses, so you cannot create a course site in bCourses.</p>
    </div>
    <div v-if="size(teachingTerms)">
      <div>
        <div id="page-create-course-select-semesters" class="buttonset">
          <h2 class="page-create-course-site-header page-create-course-site-header2">Term</h2>
          <span v-for="(term, index) in teachingTerms" :key="index">
            <v-btn
              :id="`term${index}`"
              name="term"
              :aria-selected="currentSemester === term.slug"
              :color="currentSemester === term.slug ? 'primary' : ''"
              role="tab"
              @click="switchSemester(term)"
              @keyup.enter="switchSemester(term)"
            >
              {{ term.name }}
            </v-btn>
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
          <v-expansion-panels v-if="coursesList.length > 0" class="pb-4" multiple>
            <v-expansion-panel
              v-for="course in coursesList"
              :id="`sections-course-${course.slug}`"
              :key="course.course_id"
              class="container px-1 mt-4"
              style="border-radius: 3px !important"
              :value="course.slug"
            >
              <v-expansion-panel-title class="d-flex align-start justify-start height-unset pa-0">
                <template #actions="{ expanded }">
                  <v-icon class="mt-1 order-0" :icon="expanded ? ' mdi-menu-down' : 'mdi-menu-right'" />
                </template>
                <h3 class="d-flex flex-nowrap order-1 sections-course-title">
                  {{ course.courseCode }}
                  <span v-if="course.title">: {{ course.title }}</span>
                  <span v-if="size(course.sections)" class="btn-course-title-text pt-1">
                    ({{ pluralize('section', course.sections.length, {0: 'No', 1: 'One'}) }})
                  </span>
                </h3>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-row no-gutters>
                  <v-col md="12">
                    <CourseSectionsTable
                      :key="course.slug"
                      mode="createCourseForm"
                      :sections="course.sections"
                      :update-selected="updateSelected"
                    />
                  </v-col>
                </v-row>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
          <div class="d-flex justify-end">
            <v-btn
              id="page-create-course-site-cancel"
              aria-label="Cancel and return to Site Creation Overview"
              variant="text"
              @click="cancel"
            >
              Cancel
            </v-btn>
            <v-btn
              id="page-create-course-site-continue"
              aria-controls="page-create-course-site-steps-container"
              aria-label="Continue to next step"
              color="primary"
              :disabled="!selectedSectionsList.length"
              @click="showConfirmation"
            >
              Next
            </v-btn>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import OutboundLink from '@/components/utils/OutboundLink'
import {pluralize} from '@/utils'
import {size} from 'lodash'

export default {
  name: 'SelectSectionsStep',
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
    teachingTerms: {
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
      this.$router.push({path: '/create_site'})
    },
    pluralize,
    size,
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

<style lang="scss">
.page-create-course-site-select-sections {
  .v-expansion-panel-title__overlay {
    background-color: transparent !important;
  }
  .v-expansion-panel-text__wrapper {
    padding: 6px 4px 0px 4px;
  }
  .v-expansion-panel-title__icon {
    margin-inline-start: unset;
  }
  .v-expansion-panel__shadow {
    display: none !important;
  }
  .v-expansion-panel::after {
    border: none !important;
  }
}
</style>
