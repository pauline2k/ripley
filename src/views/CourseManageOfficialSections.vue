<template>
  <div class="canvas-application page-course-official-sections">
    <div v-if="feedFetched && !displayError">
      <div v-if="currentWorkflowStep === 'staging'">
        <MaintenanceNotice course-action-verb="site is updated" />
      </div>

      <h1 class="page-course-official-sections-header1">Official Sections</h1>

      <div v-if="currentWorkflowStep === 'preview'">
        <v-alert
          id="page-course-official-sections-job-status-notice"
          v-model="showAlert"
          class="d-flex align-center justify-space-between my-2"
          closable
          close-label="Hide notice"
          :color="jobStatus !== 'sectionEditsCompleted' ? 'error' : 'success'"
          density="compact"
          role="alert"
          variant="tonal"
        >
          {{ jobStatusMessage }}
        </v-alert>

        <h2 class="sr-only">Viewing Sections</h2>

        <div class="page-course-official-sections-sections-area page-course-official-sections-current-sections-white-border">
          <v-row no-gutters class="page-course-official-sections-current-sections-header">
            <v-col md="4">
              <h3 class="page-course-official-sections-existing-sections-header-label">
                Sections in this Course Site
              </h3>
            </v-col>
            <v-col md="8" class="text-right">
              <v-btn
                v-if="canvasSite.canEdit"
                class="canvas-button canvas-button-primary canvas-no-decoration page-course-official-sections-button"
                @click="changeWorkflowStep('staging')"
              >
                Edit Sections
              </v-btn>
            </v-col>
          </v-row>
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
          <h2 class="sr-only">Managing Sections</h2>

          <v-row no-gutters class="row page-course-official-sections-current-sections-header">
            <v-col md="4">
              <h3 class="page-course-official-sections-existing-sections-header-label">
                Sections in this Course Site
              </h3>
            </v-col>
            <v-col md="8" class="text-right">
              <v-btn
                class="canvas-button mx-1"
                aria-label="Cancel section modifications for this course site"
                @click="cancel"
              >
                Cancel
              </v-btn>
              <v-btn
                class="canvas-button canvas-button-primary"
                :disabled="totalStagedCount === 0"
                aria-label="Apply pending modifications to this course site"
                @click="saveChanges"
              >
                Save Changes
              </v-btn>
            </v-col>
          </v-row>
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
              ></CourseSectionsTable>
            </v-col>
          </v-row>
          <v-row v-if="currentStagedCount() > 12" class="row">
            <v-col md="12" class="text-right">
              <v-btn
                class="canvas-button canvas-no-decoration"
                aria-label="Cancel section modifications for this course site"
                @click="changeWorkflowStep('preview')"
              >
                Cancel
              </v-btn>
              <v-btn
                :disabled="totalStagedCount === 0"
                class="canvas-button canvas-button-primary canvas-no-decoration"
                aria-label="Apply pending modifications to this course site"
                @click="saveChanges"
              >
                Save Changes
              </v-btn>
            </v-col>
          </v-row>
        </div>
        <div class="page-course-official-sections-sections-area">
          <v-row no-gutters>
            <v-col md="12">
              <h3 class="page-course-official-sections-available-sections-header-label">
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
              v-for="course in courseSemesterClasses"
              :id="`sections-course-${course.slug}`"
              :key="course.courseCode"
              class="sections-course-container px-1 mt-4"
              style="border-radius: 3px !important"
              :value="course.slug"
            >
              <v-expansion-panel-title class="d-flex flex-row-reverse height-unset pa-0">
                <div class="d-flex flex-wrap flex-grow-1">
                  <h3 class="sections-course-title">
                    {{ course.courseCode }}<span v-if="course.title"> : {{ course.title }}</span>
                  </h3>
                  <span v-if="course.sections && (course.sections.length === 1)" class="sections-course-subtitle text-no-wrap">&nbsp;(1 section)</span>
                  <span v-if="course.sections && (course.sections.length !== 1)" class="sections-course-subtitle text-no-wrap">&nbsp;({{ course.sections.length }} sections)</span>
                </div>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <div v-if="course.sections.length > 1" class="page-course-official-sections-form-select-all-option">
                  <v-btn
                    v-if="!allSectionsAdded(course)"
                    class="button-link page-course-official-sections-form-select-all-option-button"
                    aria-label="Add all sections for this course to the list of sections to be added"
                    @click="addAllSections(course)"
                  >
                    Add All
                  </v-btn>
                  <span v-if="allSectionsAdded(course)">All Added</span>
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
                    ></CourseSectionsTable>
                  </v-col>
                </v-row>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </div>

      <div v-if="currentWorkflowStep === 'processing'" aria-live="polite">
        <h2 class="page-course-official-sections-existing-sections-header-label">
          Updating Official Sections in Course Site
        </h2>
        <div v-if="jobStatus === 'sendingRequest'" class="page-course-official-sections-pending-request">
          <v-progress-circular
            class="mr-2"
            color="primary"
            indeterminate
          />
          Sending request...
        </div>
        <div v-if="jobStatus === 'New'" class="page-course-official-sections-pending-request">
          <v-progress-circular
            class="mr-2"
            color="primary"
            indeterminate
          />
          Request sent. Awaiting processing....
        </div>
        <div v-if="jobStatus">
          <ProgressBar :percent-complete-rounded="percentCompleteRounded" />
        </div>
      </div>
    </div>

    <div v-if="displayError" class="alert-container" role="alert">
      <i class="fa fa-warning canvas-notice-icon"></i>
      <div class="notice-text-container">
        <h1 class="notice-text-header">Error</h1>
        <p>{{ displayError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'
import ProgressBar from '@/components/bcourses/shared/ProgressBar'

import {courseProvisionJobStatus, getCourseSections, updateSiteSections} from '@/api/canvas-site'

export default {
  name: 'CourseManageOfficialSections',
  components: {
    CourseSectionsTable,
    MaintenanceNotice,
    ProgressBar
  },
  mixins: [Context],
  data: () => ({
    adminActingAs: null,
    adminSemesters: null,
    allSections: [],
    availableSectionsPanel: [],
    canvasSite: {},
    courseSemesterClasses: [],
    currentWorkflowStep: null,
    displayError: null,
    existingCourseSections: [],
    feedFetched: false,
    isAdmin: false,
    isCourseCreator: false,
    jobStatus: null,
    jobStatusMessage: '',
    percentCompleteRounded: 0,
    showAlert: false,
    totalStagedCount: 0
  }),
  created() {
    this.fetchFeed()
    this.$ready()
  },
  watch: {
    jobStatusMessage(msg) {
      if (msg.length) {
        this.showAlert = true
      }
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
      return !this.$_.find(course.sections, section => {
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
    currentStagedCount() {
      var stagedCount = 0
      this.allSections.forEach(section => {
        if ((section.isCourseSection && section.stagedState === null) || (!section.isCourseSection && section.stagedState === 'add')) {
          stagedCount++
        }
      })
      return stagedCount
    },
    expandParentClass(section) {
      section.parentClass.collapsed = false
    },
    fetchFeed() {
      getCourseSections(this.currentUser.canvasSiteId).then(
        response => {
          this.percentCompleteRounded = null
          if (response.canvasSite) {
            this.canvasSite = response.canvasSite
            this.refreshFromFeed(response)
          } else {
            this.displayError = 'Failed to retrieve section data.'
          }
        },
        this.$errorHandler
      )
    },
    getStagedSections() {
      const sections = {
        addSections: [],
        deleteSections: [],
        updateSections: []
      }
      this.courseSemesterClasses.forEach(classItem => {
        classItem.sections.forEach(section => {
          if (section.stagedState === 'add') {
            sections.addSections.push(section.id)
          } else if (section.stagedState === 'delete') {
            sections.deleteSections.push(section.id)
          } else if (section.stagedState === 'update') {
            sections.updateSections.push(section.id)
          }
        })
      })
      return sections
    },
    loadCourseLists(teachingTerms) {
      const courseSemester = this.$_.find(teachingTerms, semester => {
        return (this.$_.toString(semester.termId) === this.$_.toString(this.canvasSite.term.id))
      })
      if (courseSemester) {
        this.availableSectionsPanel = []
        this.courseSemesterClasses = courseSemester.classes
        this.usersClassCount = this.courseSemesterClasses.length
        this.existingCourseSections = this.canvasSite.officialSections
        this.allSections = []
        const existingSectionIds = this.$_.map(this.existingCourseSections, 'id')
        this.courseSemesterClasses.forEach(classItem => {
          classItem.sections.forEach(teachingSection => {
            teachingSection.parentClass = classItem
            this.allSections.push(teachingSection)
            teachingSection.stagedState = null
            if (teachingSection.isCourseSection) {
              this.availableSectionsPanel = [classItem.slug]
            }
            this.canvasSite.officialSections.forEach(officialSection => {
              if (officialSection.id === teachingSection.id && existingSectionIds.indexOf(teachingSection.id) === -1) {
                if (officialSection.canvasName !== `${teachingSection.courseCode} ${teachingSection.name}`) {
                  this.$_.set(teachingSection, 'nameDiscrepancy', true)
                }
              }
            })
          })
        })
      } else {
        this.usersClassCount = 0
      }
    },
    refreshFromFeed(feed) {
      if (feed.teachingTerms) {
        this.loadCourseLists(feed.teachingTerms)
      }
      this.isAdmin = feed.is_admin
      this.adminActingAs = feed.admin_acting_as
      this.adminSemesters = feed.admin_semesters
      this.isCourseCreator = this.usersClassCount > 0
      this.feedFetched = true
      this.currentWorkflowStep = 'preview'
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
      this.changeWorkflowStep('processing')
      this.jobStatus = 'sendingRequest'
      const update = this.getStagedSections()
      updateSiteSections(
        this.currentUser.canvasSiteId,
        update.addSections,
        update.deleteSections,
        update.updateSections
      ).then(
        response => {
          this.backgroundJobId = response.job_id
          // this.trackSectionUpdateJob()
          this.jobStatus = response.jobStatus
        }
      ).catch(
        error => {
          this.jobStatus = 'error'
          this.jobStatusMessage = error
        }
      )
    },
    sectionString(section) {
      return section.courseCode + ' ' + section.section_label + ' (Section ID: ' + section.id + ')'
    },
    stageAdd(section) {
      if (!section.isCourseSection) {
        this.$_.set(section, 'stagedState', 'add')
        this.$announcer.polite('Included in the list of sections to be added')
      } else {
        this.displayError = 'Unable to add ' + this.sectionString(section) + ', as it already exists within the course site.'
      }
      this.updateStagedCount()
    },
    stageDelete(section) {
      if (section.isCourseSection) {
        this.expandParentClass(section)
        this.$_.set(section, 'stagedState', 'delete')
        this.$announcer.polite('Included in the list of sections to be deleted')
      } else {
        this.displayError = 'Unable to delete Section ID ' + this.sectionString(section) + ' which does not exist within the course site.'
      }
      this.updateStagedCount()
    },
    stageUpdate(section) {
      if (section.isCourseSection) {
        this.expandParentClass(section)
        this.$_.set(section, 'stagedState', 'update')
        this.$announcer.polite('Included in the list of sections to be updated')
      } else {
        this.displayError = 'Unable to update Section ID ' + this.sectionString(section) + ' which does not exist within the course site.'
      }
      this.updateStagedCount()
    },
    trackSectionUpdateJob() {
      this.exportTimer = setInterval(() => {
        courseProvisionJobStatus(this.backgroundJobId).then(
          response => {
            this.jobStatus = response.jobStatus
            this.percentCompleteRounded = Math.round(response.percentComplete * 100)
            if (this.jobStatus !== 'New' && this.jobStatus !== 'Processing') {
              this.percentCompleteRounded = null
              clearInterval(this.exportTimer)
              if (this.jobStatus === 'Completed') {
                this.jobStatusMessage = 'The sections in this course site have been updated successfully.'
              } else {
                this.jobStatusMessage = 'An error has occurred with your request. Please try again or contact bCourses support.'
              }
              this.fetchFeed()
            }
          },
          this.$errorHandler
        )
      }, 2000)
    },
    toggleCollapse(course) {
      this.$_.set(course, 'collapsed', !course.collapsed)
    },
    unstage(section) {
      if (section.stagedState === 'add') {
        this.expandParentClass(section)
        this.$announcer.polite('Removed section from the list of sections to be added')
      } else if (section.stagedState === 'delete') {
        this.$announcer.polite('Removed section from the list of sections to be deleted')
      } else if (section.stagedState === 'update') {
        this.$announcer.polite('Removed section from the list of sections to be updated')
      }
      section.stagedState = null
      this.updateStagedCount()
    },
    unstageAll() {
      this.courseSemesterClasses.forEach(classItem => {
        classItem.sections.forEach(section => {
          section.stagedState = null
        })
      })
      this.updateStagedCount()
    },
    updateStagedCount() {
      var stagedCount = 0
      this.allSections.forEach(section => {
        if (section.stagedState !== null) {
          stagedCount++
        }
      })
      this.totalStagedCount = stagedCount
    }
  }
}
</script>

<style scoped lang="scss">
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

  .page-course-official-sections-button {
    white-space: nowrap;
  }

  .page-course-official-sections-courses-container {
    margin: 0;
  }

  .page-course-official-sections-current-sections-grey-border {
    border: $color-grey-area-border-dark solid 1px;
    .page-course-official-sections-courses-container {
      margin-bottom: 15px;
    }

    .page-course-official-sections-existing-sections-header-label {
      margin-top: 3px;
    }
  }

  .page-course-official-sections-current-course {
    margin-left: 0;
    margin-top: 10px;
  }

  .page-course-official-sections-current-sections-header {
    margin-bottom: 5px;
  }

  .page-course-official-sections-current-sections-white-border {
    border: $color-white solid 1px;
  }

  .page-course-official-sections-sections-area.page-course-official-sections-current-sections-grey-border {
    padding: 15px;
  }

  .page-course-official-sections-sections-area + .page-course-official-sections-sections-area {
    margin-top: 25px;
  }

  .page-course-official-sections-existing-sections-header-label {
    font-size: 19px;
    margin-top: 10px;
  }

  .page-course-official-sections-available-sections-header-label {
    font-size: 19px;
    margin-bottom: 15px;
  }

  .page-course-official-sections-form-select-all-option {
    font-size: 12px;
    margin: 6px 0 4px 2px;
  }

  .page-course-official-sections-form-select-all-option-button {
    outline: none;
  }

  .page-course-official-sections-pending-request {
    margin: 20px 0;
  }

  @media #{$small-only} {
    .page-course-official-sections-small-only-align-left {
      text-align: left;
    }
  }
  h3.sections-course-title {
    display: inline !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    line-height: 20px;
  }
  .sections-course-subtitle {
    font-size: 14px !important;
    font-weight: 400;
    line-height: 20px;
  }
}
</style>

<style lang="scss">
.page-course-official-sections {
  .v-expansion-panel-title__overlay {
    background-color: transparent !important;
  }
  .v-expansion-panel-text__wrapper {
    padding: 6px 4px 0px 4px;
  }
  .v-expansion-panel__shadow {
    display: none !important;
  }
  .v-expansion-panel::after {
    border: none !important;
  }
}
</style>
