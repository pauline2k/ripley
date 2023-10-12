<template>
  <div v-if="!isLoading" class="pt-3 px-6">
    <div v-if="feedFetched && !displayError">
      <Header1 class="mb-2 mt-0" :text="`${canvasSite.name}, ${canvasSite.term.name}`" />
      <div class="align-center d-flex h2-container justify-space-between">
        <div class="pr-2">
          <h2>Official Sections</h2>
        </div>
        <div v-if="canvasSite.canEdit && currentWorkflowStep === 'preview'">
          <v-btn
            id="official-sections-edit-btn"
            class="text-no-wrap"
            color="primary"
            @click="changeWorkflowStep('staging')"
          >
            Edit Sections
          </v-btn>
        </div>
      </div>
      <MaintenanceNotice class="mt-3" course-action-verb="site is updated" />
      <div class="mb-8">
        <div v-if="currentWorkflowStep === 'preview'">
          <v-alert
            id="page-course-official-sections-job-status-notice"
            v-model="showAlert"
            class="my-2"
            closable
            close-label="Hide notice"
            density="compact"
            role="alert"
            :type="jobStatus !== 'finished' ? 'error' : 'success'"
            variant="tonal"
          >
            <div class="font-size-16">{{ jobStatusMessage }}</div>
          </v-alert>
          <CourseSectionsTable
            class="mb-1 mt-4"
            mode="preview"
            :row-class-logic="rowClassLogic"
            :row-display-logic="rowDisplayLogic"
            :sections="existingCourseSections"
          />
        </div>
        <div v-if="currentWorkflowStep === 'staging'">
          <h3 class="sr-only">Managing Sections</h3>
          <div class="float-right py-3">
            <v-btn
              id="official-sections-save-btn"
              class="mr-1 text-no-wrap"
              color="primary"
              :disabled="totalStagedCount === 0"
              @click="saveChanges"
            >
              Save Changes
            </v-btn>
            <v-btn
              id="official-sections-cancel-btn"
              variant="text"
              @click="cancel"
            >
              Cancel
            </v-btn>
          </div>
          <CourseSectionsTable
            class="mb-1"
            mode="currentStaging"
            :row-class-logic="rowClassLogic"
            :row-display-logic="rowDisplayLogic"
            :sections="allSections"
            :stage-delete-action="stageDelete"
            :stage-update-action="stageUpdate"
            :unstage-action="unstage"
          />
          <div v-if="totalStagedCount > 12">
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
          </div>
          <div>
            <div class="mb-3 mt-8">
              <h2>Sections Available to Add</h2>
            </div>
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
                    <v-icon :icon="expanded ? mdiMenuDown : mdiMenuRight" />
                  </template>
                  <h5 id="available-course-header" class="sections-course-title">
                    {{ course.courseCode }}
                    <span v-if="course.title">&mdash; {{ course.title }}</span>
                    <span v-if="size(course.sections)">
                      ({{ pluralize('section', course.sections.length, {0: 'No', 1: 'One'}) }})
                    </span>
                  </h5>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <div v-if="course.sections.length > 1">
                    <v-btn
                      :id="`course-${index}-add-all-sections-btn`"
                      aria-label="Add all sections listed below to the course site"
                      :color="allSectionsAdded(course) ? '' : 'primary'"
                      :disabled="allSectionsAdded(course)"
                      @click="addAllSections(course)"
                    >
                      <span v-if="allSectionsAdded(course)">All Added</span>
                      <span v-else>Add All</span>
                    </v-btn>
                  </div>
                  <v-row no-gutters>
                    <v-col md="12">
                      <CourseSectionsTable
                        class="mb-1 mt-4"
                        mode="availableStaging"
                        :row-class-logic="rowClassLogic"
                        :row-display-logic="rowDisplayLogic"
                        :sections="course.sections"
                        :stage-add-action="stageAdd"
                        :unstage-action="unstage"
                      />
                    </v-col>
                  </v-row>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
        </div>
        <div v-if="currentWorkflowStep === 'processing'" aria-live="polite">
          <h3 id="updating-sections-header" class="mt-6 text-no-wrap">
            Updating Official Sections in Course Site
          </h3>
          <div class="py-3">
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
          <v-progress-linear
            color="primary"
            height="10"
            indeterminate
          />
        </div>
      </div>
    </div>
    <div v-if="displayError" role="alert">
      <v-icon :icon="mdiAlertCircleOutline" color="red" />
      <div>
        <Header1 class="notice-text-header" text="Error" />
        <p>{{ displayError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import Header1 from '@/components/utils/Header1.vue'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'
import {mdiAlertCircleOutline, mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {pluralize} from '@/utils'
</script>

<script>
import Context from '@/mixins/Context'
import {courseProvisionJobStatus, getCourseSections, updateSiteSections} from '@/api/canvas-site'
import {toInt} from '@/utils'
import {each, filter, find, flatMap, get, includes, keys, set, size, toString, union, unset} from 'lodash'

export default {
  name: 'ManageOfficialSections',
  mixins: [Context],
  data: () => ({
    adminActingAs: null,
    adminTerms: null,
    availableSectionsPanel: [],
    canvasSite: undefined,
    canvasSiteId: undefined,
    courseSemesterClasses: [],
    currentWorkflowStep: null,
    displayError: null,
    existingCourseSections: [],
    feedFetched: false,
    isAdmin: false,
    isCourseCreator: false,
    jobStatus: null,
    jobStatusMessage: ''
  }),
  created() {
    this.canvasSiteId = toInt(get(this.$route, 'params.canvasSiteId'))
    this.fetchFeed().finally(() => {
      this.$ready()
    })
  },
  computed: {
    allSections() {
      return flatMap(this.courseSemesterClasses, classItem => {
        return classItem.sections
      })
    },
    showAlert: {
      get() {
        return !!size(this.jobStatusMessage)
      },
      set(show) {
        if (!show) {
          this.jobStatusMessage = ''
        }
      }
    },
    totalStagedCount() {
      return size(filter(this.allSections, section => {
        return (section.isCourseSection && includes(keys(section), 'stagedState')) || (!section.isCourseSection && section.stagedState === 'add')
      }))
    }
  },
  methods: {
    addAllSections(course) {
      this.alertScreenReader('All sections selected for course: ' + course.title)
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
        this.alertScreenReader('Edit section form loaded')
        this.jobStatus = null
        this.jobStatusMessage = ''
      } else if (step === 'preview') {
        this.alertScreenReader('Read only section list loaded')
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
        this.alertScreenReader('Included in the list of sections to be added')
      } else {
        this.displayError = 'Unable to add ' + this.sectionString(section) + ', as it already exists within the course site.'
      }
    },
    stageDelete(section) {
      if (section.isCourseSection) {
        this.availableSectionsPanel = union(this.availableSectionsPanel, [section.courseSlug])
        set(section, 'stagedState', 'delete')
        this.alertScreenReader('Included in the list of sections to be deleted')
      } else {
        this.displayError = 'Unable to delete Section ID ' + this.sectionString(section) + ' which does not exist within the course site.'
      }
    },
    stageUpdate(section) {
      if (section.isCourseSection) {
        this.availableSectionsPanel = union(this.availableSectionsPanel, [section.courseSlug])
        set(section, 'stagedState', 'update')
        this.alertScreenReader('Included in the list of sections to be updated')
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
        this.alertScreenReader('Removed section from the list of sections to be added')
      } else if (section.stagedState === 'delete') {
        this.alertScreenReader('Removed section from the list of sections to be deleted')
      } else if (section.stagedState === 'update') {
        this.alertScreenReader('Removed section from the list of sections to be updated')
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
.h2-container {
  min-height: 36px;
}
h5.sections-course-title {
  font-size: 18px !important;
  font-weight: 400 !important;
  line-height: 18px;
}
@media #{$small-only} {
  .page-course-official-sections-small-only-align-left {
    text-align: left;
  }
}
</style>
