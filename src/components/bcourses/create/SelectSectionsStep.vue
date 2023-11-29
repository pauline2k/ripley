<template>
  <div>
    <div v-if="!size(teachingTerms)" role="alert">
      You are currently not listed as the instructor of record for any courses, so you cannot create a course site in bCourses.
    </div>
    <div v-if="size(teachingTerms)">
      <v-tabs
        v-if="size(teachingTerms) > 1"
        v-model="selectedTerm"
        aria-label="Official Sections"
        selected-class="selected-term-tab"
      >
        <v-tab
          v-for="(term, index) in teachingTerms"
          :id="`term${index}`"
          :key="index"
          aria-controls="official-sections-tabpanel"
          :aria-selected="term.slug === selectedTerm"
          class="rounded"
          :tabindex="term.slug === selectedTerm ? 0 : -1"
          :value="term.slug"
        >
          {{ term.name }}
        </v-tab>
      </v-tabs>
      <v-card class="pa-3">
        <v-window
          id="official-sections-tabpanel"
          v-model="selectedTerm"
          :aria-labelledby="size(teachingTerms) > 1 ? `term${findIndex(teachingTerms, t => t.slug === selectedTerm)}` : undefined"
          :role="size(teachingTerms) > 1 ? 'tabpanel' : undefined"
        >
          <v-window-item :value="selectedTerm">
            <h2 id="official-sections-heading">{{ selectedTermName }} Official Sections</h2>
            <div class="text-subtitle-1 mt-1 mb-3">
              All official sections you select below will be put in ONE, single course site.
            </div>
            <v-alert
              class="mt-2"
              closable
              close-label="Hide help"
              @click:close="onCloseHelp"
            >
              <div class="d-flex">
                <div class="pr-2">
                  <v-icon
                    class="left page-help-notice-icon"
                    color="grey"
                    :icon="mdiHelpCircleOutline"
                  />
                </div>
                <div>
                  <div class="font-weight-medium">
                    Need help deciding which official sections to select?
                  </div>
                  If you have a course with multiple sections, you will need to decide whether you want to:
                  <div class="mt-1">
                    1. Create one, single course site which includes official sections for both your primary and secondary sections, or
                  </div>
                  <div>
                    2. Create multiple course sites, perhaps with one for each section, or
                  </div>
                  <div>
                    3. Create separate course sites based on instruction mode.
                    <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0010732#instructionmode">
                      Learn more about instruction modes in bCourses.
                    </OutboundLink>
                  </div>
                </div>
              </div>
            </v-alert>
            <v-expansion-panels
              v-if="size(coursesList)"
              v-model="panels"
              class="my-5"
              multiple
            >
              <v-expansion-panel
                v-for="course in coursesList"
                :id="`sections-course-${course.slug}`"
                :key="course.course_id"
                :value="course.slug"
                bg-color="blue-lighten-5"
              >
                <v-expansion-panel-title :id="`sections-course-${course.slug}-btn`">
                  <template #actions="{ expanded }">
                    <v-icon :icon="expanded ? mdiMenuDown : mdiMenuRight" />
                  </template>
                  <span
                    :aria-level="teachingTerms.length === 1 ? 3 : 4"
                    class="sections-course-title"
                    role="heading"
                  >
                    <CourseCodeAndTitle :course="course" />
                  </span>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <CourseSectionsTable
                    :id="`template-sections-table-${course.slug}`"
                    :key="course.slug"
                    class="mb-1 mt-4"
                    mode="createCourseForm"
                    :sections="course.sections"
                    :table-caption="courseSectionsTableCaption(course)"
                    table-clazz="border-0"
                    :update-selected="updateSelected"
                  />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-window-item>
        </v-window>
        <div class="d-flex justify-end mb-2">
          <v-btn
            id="page-create-course-site-continue"
            aria-label="Continue to next step"
            class="mr-1"
            color="primary"
            :disabled="!selectedSectionsList.length"
            @click="showConfirmation"
          >
            Next
          </v-btn>
          <v-btn
            id="page-create-course-site-cancel"
            aria-label="Cancel and return to Site Creation Overview"
            variant="tonal"
            @click="cancel"
          >
            Cancel
          </v-btn>
        </div>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import CourseCodeAndTitle from '@/components/bcourses/create/CourseCodeAndTitle.vue'
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import {mdiHelpCircleOutline, mdiMenuDown, mdiMenuRight} from '@mdi/js'
import OutboundLink from '@/components/utils/OutboundLink'
</script>

<script>
import Context from '@/mixins/Context.vue'
import {get, find, findIndex, size} from 'lodash'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'SelectSectionsStep',
  mixins: [Context],
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
    panels: [],
    selectedTerm: undefined
  }),
  computed: {
    isAdmin() {
      return this.currentUser.isAdmin || this.currentUser.isCanvasAdmin
    },
    selectedTermName() {
      const term = find(this.teachingTerms, t => t.slug === this.selectedTerm)
      return get(term, 'name', '')
    }
  },
  watch: {
    selectedTerm(slug) {
      this.switchSemester(slug)
    }
  },
  created() {
    this.selectedTerm = this.currentSemester
    if (this.selectedSectionsList.length) {
      this.panels = Array.from({length: this.coursesList.length}, (value, index) => index)
    } else if (this.coursesList.length === 1) {
      this.panels = [0]
    }
  },
  methods: {
    cancel() {
      this.$router.push({path: '/manage_sites'})
    },
    courseSectionsTableCaption(course) {
      let caption = 'Official sections in this course. Use the checkboxes in the Action column to select sections'
      if (size(course.sections) > 1) {
        caption += ', or use the "Select All" button above.'
      }
      return caption
    },
    findIndex,
    onCloseHelp() {
      this.alertScreenReader('help hidden')
      putFocusNextTick(size(this.coursesList) ? `sections-course-${get(this.coursesList, '0.slug')}-btn` : 'page-create-course-site-cancel')
    },
    size
  }
}
</script>

<style scoped lang="scss">
.sections-course-title {
  font-size: 15px !important;
  font-weight: 700 !important;
  line-height: 15px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.selected-term-tab {
  background-color: $color-primary;
  color: $color-white !important;
}
</style>
<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type -->
<style>
.v-expansion-panel-text__wrapper {
  padding: 8px 12px 16px !important;
}
</style>
