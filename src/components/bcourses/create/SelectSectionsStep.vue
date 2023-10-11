<template>
  <div>
    <div v-if="!size(teachingTerms)" role="alert">
      You are currently not listed as the instructor of record for any courses, so you cannot create a course site in bCourses.
    </div>
    <div v-if="size(teachingTerms)">
      <h2 v-if="isAdmin && teachingTerms.length > 1">Term</h2>
      <div :class="{'py-2': isAdmin}">
        <v-btn-toggle
          v-if="teachingTerms.length > 1"
          v-model="slug"
          class="term-btn-toggle"
          color="primary"
        >
          <v-btn
            v-for="(term, index) in teachingTerms"
            :id="`term${index}`"
            :key="index"
            :value="term.slug"
          >
            {{ term.name }}
          </v-btn>
        </v-btn-toggle>
        <div :class="{'mt-5': teachingTerms.length > 1}">
          <h2 v-if="teachingTerms.length === 1">{{ teachingTerms[0].name }} Official Sections</h2>
          <h3 v-if="teachingTerms.length > 1">Official Sections</h3>
          <div class="text-subtitle-1">
            All official sections you select below will be put in ONE, single course site.
          </div>
          <v-alert class="mt-2" closable color="alert">
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
        </div>
        <v-expansion-panels
          v-if="coursesList.length > 0"
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
            <v-expansion-panel-title>
              <template #actions="{ expanded }">
                <v-icon :icon="expanded ? mdiMenuDown : mdiMenuRight" />
              </template>
              <h3 v-if="teachingTerms.length === 1">
                <CourseCodeAndTitle :course="course" />
              </h3>
              <h4 v-if="teachingTerms.length > 1">
                <CourseCodeAndTitle :course="course" />
              </h4>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <CourseSectionsTable
                :key="course.slug"
                class="mb-1 mt-4"
                mode="createCourseForm"
                :sections="course.sections"
                :update-selected="updateSelected"
              />
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
        <div class="d-flex justify-end mb-4">
          <v-btn
            id="page-create-course-site-continue"
            aria-label="Continue to next step"
            color="primary"
            :disabled="!selectedSectionsList.length"
            @click="showConfirmation"
          >
            Next
          </v-btn>
          <v-btn
            id="page-create-course-site-cancel"
            aria-label="Cancel and return to Site Creation Overview"
            variant="text"
            @click="cancel"
          >
            Cancel
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiHelpCircleOutline, mdiMenuDown, mdiMenuRight} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context.vue'
import CourseCodeAndTitle from '@/components/bcourses/create/CourseCodeAndTitle.vue'
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import OutboundLink from '@/components/utils/OutboundLink'
import {find, size} from 'lodash'

export default {
  name: 'SelectSectionsStep',
  mixins: [Context],
  components: {CourseCodeAndTitle, CourseSectionsTable, OutboundLink},
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
    term: undefined
  }),
  computed: {
    isAdmin() {
      return this.currentUser.isAdmin || this.currentUser.isCanvasAdmin
    },
    slug: {
      get() {
        return this.currentSemester
      },
      set(slug) {
        if (slug !== this.currentSemester.slug) {
          const term = find(this.teachingTerms, ['slug', slug])
          this.switchSemester(term)
        }
      }
    }
  },
  created() {
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
    size
  }
}
</script>

<style scoped lang="scss">
.term-btn-toggle {
  border-width: 1px;
}
</style>
