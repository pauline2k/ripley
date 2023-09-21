<template>
  <div>
    <div v-if="!size(teachingTerms)" role="alert">
      You are currently not listed as the instructor of record for any courses, so you cannot create a course site in bCourses.
    </div>
    <div v-if="size(teachingTerms)">
      <h2>Term</h2>
      <div class="pl-3 py-2">
        <v-btn-toggle
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
        <div class="mt-5">
          <h3>Official Sections</h3>
          <div class="pb-2 text-subtitle-1">
            All official sections you select below will be put in ONE, single course site.
          </div>
          <v-alert closable color="alert">
            <div class="align-center d-flex">
              <div class="pr-1">
                <v-icon
                  class="left page-help-notice-icon"
                  color="grey"
                  icon="mdi-help-circle-outline"
                />
              </div>
              <div>
                Need help deciding which official sections to select?
              </div>
            </div>
            <div class="pl-8">
              <div>
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
          </v-alert>
        </div>
        <v-expansion-panels
          v-if="coursesList.length > 0"
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
                <v-icon :icon="expanded ? ' mdi-menu-down' : 'mdi-menu-right'" />
              </template>
              <h3>
                {{ course.courseCode }}
                <span v-if="course.title">: {{ course.title }}</span>
                <span v-if="size(course.sections)">
                  ({{ pluralize('section', course.sections.length, {0: 'No', 1: 'One'}) }})
                </span>
              </h3>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <CourseSectionsTable
                :key="course.slug"
                mode="createCourseForm"
                :sections="course.sections"
                :update-selected="updateSelected"
              />
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
            aria-label="Continue to next step"
            color="primary"
            :disabled="!selectedSectionsList.length"
            @click="showConfirmation"
          >
            Next
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import OutboundLink from '@/components/utils/OutboundLink'
import {pluralize} from '@/utils'
import {find, size} from 'lodash'

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
    term: undefined
  }),
  computed: {
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
  methods: {
    cancel() {
      this.$router.push({path: '/create_site'})
    },
    pluralize,
    size
  }
}
</script>

<style scoped lang="scss">
.term-btn-toggle {
  border-width: 1px;
}
</style>
