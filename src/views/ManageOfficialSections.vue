<template>
  <div v-if="!isLoading" class="page-course-official-sections">
    <div v-if="feedFetched && !displayError">
      <div v-if="currentWorkflowStep === 'staging'">
        <MaintenanceNotice course-action-verb="site is updated" />
      </div>
      <Header1 class="page-course-official-sections-header1" text="Official Sections" />
      <div v-if="currentWorkflowStep === 'preview'">
        <v-alert
          id="page-course-official-sections-job-status-notice"
          v-model="showAlert"
          class="d-flex align-center justify-space-between my-2"
          closable
          close-label="Hide notice"
          :type="jobStatus !== 'finished' ? 'error' : 'success'"
          density="compact"
          role="alert"
          variant="tonal"
        >
          <div class="font-size-16">{{ jobStatusMessage }}</div>
        </v-alert>
        <h2 id="sr-context-header" class="sr-only">Viewing Sections</h2>
        <div class="page-course-official-sections-sections-area page-course-official-sections-current-sections-white-border">
          <div class="d-flex align-start justify-space-between pb-2">
            <h3 id="course-site-sections-header">
              Sections in this Course Site
            </h3>
            <div class="d-flex align-end">
              <v-btn
                v-if="canvasSite.canEdit"
                id="official-sections-edit-btn"
                class="canvas-no-decoration text-no-wrap"
                color="primary"
                @click="changeWorkflowStep('staging')"
              >
                Edit Sections
              </v-btn>
            </div>
          </div>
          <v-row no-gutters class="page-course-official-sections-courses-container">
            <v-col md="12" class="page-course-official-sections-current-course">
              <CourseSectionsTable
                mode="preview"
                :sections="existingCourseSections"
                :row-class-logic="rowClassLogic"
                :row-display-logic="rowDisplayLogic"
              />
            </v-col>
          </v-row>
        </div>
      </div>
      <div v-if="currentWorkflowStep === 'staging'">
        <div class="page-course-official-sections-sections-area page-course-official-sections-current-sections-grey-border">
          <h2 id="sr-context-header" class="sr-only">Managing Sections</h2>
          <div class="d-flex align-center flex-wrap justify-space-between">
            <h3 id="course-site-sections" class="text-no-wrap mb-2">
              Sections in this Course Site
            </h3>
            <div class="mb-2 ml-auto">
              <v-btn
                id="official-sections-cancel-btn"
                class="mx-1"
                aria-label="Cancel section modifications for this course site"
                @click="cancel"
              >
                Cancel
              </v-btn>
              <v-btn
                id="official-sections-save-btn"
                aria-label="Apply pending modifications to this course site"
                class="text-no-wrap"
                color="primary"
                :disabled="totalStagedCount === 0"
                @click="saveChanges"
              >
                Save Changes
              </v-btn>
            </div>
          </div>
          <v-row no-gutters class="page-course-official-sections-courses-container">
            <v-col md="12" class="page-course-official-sections-current-course">
              <CourseSectionsTable
                mode="currentStaging"
                :sections="allSections"
                :unstage-action="unstage"
                :stage-delete-action="stageDelete"
                :stage-update-action="stageUpdate"
                :row-class-logic="rowClassLogic"
                :row-display-logic="rowDisplayLogic"
              />
            </v-col>
          </v-row>
          <v-row v-if="totalStagedCount > 12" class="row">
            <v-col md="12" class="text-right">
              <v-btn
                id="official-sections-secondary-cancel-btn"
                aria-label="Cancel section modifications for this course site"
                class="mx-1"
                @click="cancel"
              >
                Cancel
              </v-btn>
              <v-btn
                id="official-sections-secondary-save-btn"
                aria-label="Apply pending modifications to this course site"
                :disabled="totalStagedCount === 0"
                class="text-no-wrap"
                color="primary"
                @click="saveChanges"
              >
                Save Changes
              </v-btn>
            </v-col>
          </v-row>
        </div>
        <div class="page-course-official-sections-sections-area mt-5">
          <v-row no-gutters>
            <v-col md="12">
              <h3 id="available-sections-header" class="page-course-official-sections-available-sections-header-label">
                All sections available to add to this Course Site
              </h3>
            </v-col>
          </v-row>
          <v-expansion-panels
            v-if="courseSemesterClasses.length > 0"
            v-model="availableSectionsPanel"
            multiple
          >
            <v-expansion-panel
              v-for="(course, index) in courseSemesterClasses"
              :id="`sections-course-${course.slug}`"
              :key="index"
              bg-color="blue-lighten-5"
              :value="course.slug"
            >
              <v-expansion-panel-title>
                <template #actions="{ expanded }">
                  <v-icon :icon="expanded ? ' mdi-menu-down' : 'mdi-menu-right'" />
                </template>
                <h4 id="available-course-header" class="sections-course-title">
                  {{ course.courseCode }}
                  <span v-if="course.title">: {{ course.title }}</span>
                  <span v-if="size(course.sections)">
                    ({{ pluralize('section', course.sections.length, {0: 'No', 1: 'One'}) }})
                  </span>
                </h4>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <div v-if="course.sections.length > 1">
                  <v-btn
                    :id="`course-${index}-add-all-sections-btn`"
                    aria-label="Add all sections for this course to the list of sections to be added"
                    class="course-add-all-sections-btn"
                    :color="allSectionsAdded(course) ? '' : 'primary'"
                    :disabled="allSectionsAdded(course)"
                    variant="plain"
                    @click="addAllSections(course)"
                  >
                    <template v-if="allSectionsAdded(course)">All Added</template>
                    <template v-else>Add All</template>
                  </v-btn>
                </div>
                <v-row no-gutters>
                  <v-col md="12">
                    <CourseSectionsTable
                      mode="availableStaging"
                      :sections="course.sections"
                      :unstage-action="unstage"
                      :stage-add-action="stageAdd"
                      :row-class-logic="rowClassLogic"
                      :row-display-logic="rowDisplayLogic"
                    />
                  </v-col>
                </v-row>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </div>
      <div v-if="currentWorkflowStep === 'processing'" aria-live="polite">
        <h2 id="updating-sections-header" class="text-no-wrap">
          Updating Official Sections in Course Site
        </h2>
        <div class="pending-request-step">
          <div v-if="jobStatus === 'sendingRequest'">
            Sending request...
          </div>
          <div v-if="'queued' === jobStatus">
            Request sent. Awaiting processing...
          </div>
          <div v-if="'started' === jobStatus">
            Request received. Updating sections...
          </div>
          <div v-if="'finished' === jobStatus">
            Finishing up...
          </div>
        </div>
        <div class="px-5">
          <v-progress-linear
            color="primary"
            height="10"
            indeterminate
          />
        </div>
      </div>
    </div>
    <div v-if="displayError" role="alert">
      <v-icon icon="mdi-alert-circle-outline" color="red" />
      <div>
        <Header1 class="notice-text-header" text="Error" />
        <p>{{ displayError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import Header1 from '@/components/utils/Header1.vue'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'
import {courseProvisionJobStatus, getCourseSections, updateSiteSections} from '@/api/canvas-site'
import {pluralize, toInt} from '@/utils'
import {each, filter, find, flatMap, get, includes, keys, set, size, toString, union, unset} from 'lodash'

export default {
  name: 'ManageOfficialSections',
  components: {
    Header1,
    CourseSectionsTable,
    MaintenanceNotice
  },
  mixins: [Context],
  data: () => ({
    adminActingAs: null,
    adminTerms: null,
    availableSectionsPanel: [],
    canvasSite: {},
    canvasSiteId: undefined,
    courseSemesterClasses: [],
    currentWorkflowStep: null,
    displayError: null,
    existingCourseSections: [],
    feedFetched: false,
    isAdmin: false,
    isCourseCreator: false,
    jobStatus: null,
    jobStatusMessage: '',
    showAlert: false
  }),
  created() {
    this.canvasSiteId = toInt(get(this.$route, 'params.canvasSiteId'))
    this.fetchFeed().finally(() => {
      this.$ready()
    })
  },
  watch: {
    jobStatusMessage(msg) {
      if (msg.length) {
        this.showAlert = true
      }
    }
  },
  computed: {
    allSections() {
      return flatMap(this.courseSemesterClasses, classItem => {
        return classItem.sections
      })
    },
    totalStagedCount() {
      return size(filter(this.allSections, section => {
        return (section.isCourseSection && includes(keys(section), 'stagedState')) || (!section.isCourseSection && section.stagedState === 'add')
      }))
    }
  },
  methods: {
    addAllSections(course) {
      this.$announcer.polite('All sections selected for course: ' + course.title)
      course.sections.forEach(section => {
        if (section.isCourseSection) {
          section.stagedState = null
        } else {
          section.stagedState = 'add'
        }
      })
      this.eventHub.emit('sections-table-updated')
    },
    allSectionsAdded(course) {
      return !find(course.sections, section => {
        return (!section.isCourseSection && section.stagedState !== 'add') || (section.isCourseSection && section.stagedState === 'delete')
      })
    },
    cancel() {
      this.changeWorkflowStep('preview')
      this.unstageAll()
    },
    changeWorkflowStep(step) {
      if (step === 'staging') {
        this.$announcer.polite('Edit section form loaded')
        this.jobStatus = null
        this.jobStatusMessage = ''
      } else if (step === 'preview') {
        this.$announcer.polite('Read only section list loaded')
      }
      this.currentWorkflowStep = step
    },
    fetchFeed() {
      return getCourseSections(this.canvasSiteId).then(
        response => {
          if (response.canvasSite) {
            this.canvasSite = response.canvasSite
            this.refreshFromFeed(response)
          } else {
            this.displayError = 'Failed to retrieve section data.'
          }
        }
      )
    },
    getStagedSections() {
      const sections = {
        addSections: [],
        deleteSections: [],
        updateSections: []
      }
      let valid = false
      this.courseSemesterClasses.forEach(classItem => {
        classItem.sections.forEach(section => {
          if (section.stagedState === 'add') {
            sections.addSections.push(section.id)
            valid = true
          } else if (section.stagedState === 'delete') {
            sections.deleteSections.push(section.id)
            valid = true
          } else if (section.stagedState === 'update') {
            sections.updateSections.push(section.id)
            valid = true
          }
        })
      })
      return valid ? sections : false
    },
    loadCourseLists(teachingTerms) {
      const courseSemester = find(teachingTerms, semester => {
        return (toString(semester.termId) === toString(this.canvasSite.term.id))
      })
      if (courseSemester) {
        this.availableSectionsPanel = []
        this.courseSemesterClasses = courseSemester.classes
        this.usersClassCount = this.courseSemesterClasses.length
        this.existingCourseSections = this.canvasSite.officialSections
        this.courseSemesterClasses.forEach(classItem => {
          classItem.sections.forEach(teachingSection => {
            teachingSection.courseSlug = classItem.slug
            if (teachingSection.isCourseSection) {
              this.availableSectionsPanel = [classItem.slug]
            }
            this.canvasSite.officialSections.forEach(officialSection => {
              if (officialSection.id === teachingSection.id) {
                if (officialSection.canvasName !== `${teachingSection.courseCode} ${teachingSection.name}`) {
                  set(teachingSection, 'nameDiscrepancy', true)
                }
              }
            })
          })
        })
      } else {
        this.usersClassCount = 0
      }
    },
    pluralize,
    refreshFromFeed(feed) {
      if (feed.teachingTerms) {
        this.loadCourseLists(feed.teachingTerms)
      }
      this.isAdmin = feed.is_admin
      this.adminActingAs = feed.adminActingAs
      this.adminTerms = feed.adminTerms
      this.isCourseCreator = this.usersClassCount > 0
      this.feedFetched = true
      this.changeWorkflowStep('preview')
    },
    rowClassLogic(listMode, section) {
      return {
        'template-sections-table-row-added': (listMode === 'currentStaging' && section.stagedState === 'add'),
        'template-sections-table-row-deleted': (listMode === 'availableStaging' && section.stagedState === 'delete'),
        'template-sections-table-row-disabled': (
          listMode === 'availableStaging' &&
          (
            section.stagedState === 'add' ||
            (section.isCourseSection && section.stagedState !== 'delete')
          )
        )
      }
    },
    rowDisplayLogic(listMode, section) {
      return (listMode === 'preview') ||
        (listMode === 'availableStaging') ||
        (listMode === 'currentStaging' && section && section.isCourseSection && section.stagedState !== 'delete') ||
        (listMode === 'currentStaging' && section && !section.isCourseSection && section.stagedState === 'add')
    },
    saveChanges() {
      const update = this.getStagedSections()
      if (update) {
        this.changeWorkflowStep('processing')
        this.jobStatus = 'sendingRequest'
        this.jobStatusMessage = ''
        updateSiteSections(
          this.canvasSiteId,
          update.addSections,
          update.deleteSections,
          update.updateSections
        ).then(
          response => {
            this.backgroundJobId = response.jobId
            this.jobStatus = response.jobStatus
            this.trackSectionUpdateJob()
          }
        ).catch(
          () => {
            this.changeWorkflowStep('preview')
            this.jobStatus = 'error'
            this.jobStatusMessage = 'An error has occurred with your request. Please try again or contact bCourses support.'
            clearInterval(this.exportTimer)
          }
        )
      }
    },
    sectionString(section) {
      return section.courseCode + ' ' + section.name
    },
    size,
    stageAdd(section) {
      if (!section.isCourseSection) {
        set(section, 'stagedState', 'add')
        this.$announcer.polite('Included in the list of sections to be added')
      } else {
        this.displayError = 'Unable to add ' + this.sectionString(section) + ', as it already exists within the course site.'
      }
    },
    stageDelete(section) {
      if (section.isCourseSection) {
        this.availableSectionsPanel = union(this.availableSectionsPanel, [section.courseSlug])
        set(section, 'stagedState', 'delete')
        this.$announcer.polite('Included in the list of sections to be deleted')
      } else {
        this.displayError = 'Unable to delete Section ID ' + this.sectionString(section) + ' which does not exist within the course site.'
      }
    },
    stageUpdate(section) {
      if (section.isCourseSection) {
        this.availableSectionsPanel = union(this.availableSectionsPanel, [section.courseSlug])
        set(section, 'stagedState', 'update')
        this.$announcer.polite('Included in the list of sections to be updated')
      } else {
        this.displayError = 'Unable to update Section ID ' + this.sectionString(section) + ' which does not exist within the course site.'
      }
    },
    trackSectionUpdateJob() {
      this.exportTimer = setInterval(() => {
        courseProvisionJobStatus(this.backgroundJobId).then(
          response => {
            this.jobStatus = response.jobStatus
            if (!(includes(['started', 'queued'], this.jobStatus))) {
              clearInterval(this.exportTimer)
              if (this.jobStatus === 'finished') {
                this.jobStatusMessage = 'The sections in this course site have been updated successfully.'
              } else {
                this.jobStatusMessage = 'An error has occurred with your request. Please try again or contact bCourses support.'
              }
              this.fetchFeed()
            }
          }
        ).catch(
          () => {
            this.changeWorkflowStep('preview')
            this.jobStatus = 'error'
            this.jobStatusMessage = 'An error has occurred with your request. Please try again or contact bCourses support.'
            clearInterval(this.exportTimer)
          }
        )
      }, 4000)
    },
    unstage(section) {
      if (section.stagedState === 'add') {
        this.availableSectionsPanel = union(this.availableSectionsPanel, [section.courseSlug])
        this.$announcer.polite('Removed section from the list of sections to be added')
      } else if (section.stagedState === 'delete') {
        this.$announcer.polite('Removed section from the list of sections to be deleted')
      } else if (section.stagedState === 'update') {
        this.$announcer.polite('Removed section from the list of sections to be updated')
      }
      section.stagedState = null
    },
    unstageAll() {
      return each(this.allSections, section => {
        unset(section, 'stagedState')
      })
    }
  }
}
</script>

<style scoped lang="scss">
.pending-request-step {
  height: 24px;
  margin: 20px;
  text-align: center;
}
.page-course-official-sections {
  background-color: $color-white;
  font-family: $body-font-family;
  padding: 25px;
  .button {
    padding: 10px;
  }
  .page-course-official-sections-header1 {
    font-size: 24px;
    font-weight: 400;
    line-height: 30px;
    margin: 15px 0 16px;
  }
  .page-course-official-sections-courses-container {
    margin: 0;
  }
  .page-course-official-sections-current-sections-grey-border {
    border: $color-grey-area-border-dark solid 1px;
    .page-course-official-sections-courses-container {
      margin-bottom: 15px;
    }
  }
  .page-course-official-sections-current-course {
    margin-left: 0;
    margin-top: 10px;
  }
  .page-course-official-sections-current-sections-white-border {
    border: $color-white solid 1px;
  }
  .page-course-official-sections-sections-area {
    min-width: 420px;
    .course-add-all-sections-btn:disabled {
      opacity: .5 !important;
    }
  }
  .page-course-official-sections-sections-area.page-course-official-sections-current-sections-grey-border {
    padding: 15px;
  }
  .page-course-official-sections-available-sections-header-label {
    font-size: 19px;
  }
  @media #{$small-only} {
    .page-course-official-sections-small-only-align-left {
      text-align: left;
    }
  }
  h4.sections-course-title {
    font-size: 18px !important;
    font-weight: 400 !important;
    line-height: 18px;
  }
}
</style>
