<template>
  <div class="pa-5">
    <div v-if="displayError" class="mb-2">
      <CanvasErrors :message="displayError" />
    </div>
    <div v-if="!isLoading">
      <Header1 text="Create a Course Site" />
      <MaintenanceNotice
        v-if="showMaintenanceNotice"
        class="my-2"
        course-action-verb="site is created"
      />
      <div class="pl-3">
        <CreateCourseSiteHeader
          v-if="isAdmin && currentWorkflowStep !== 'processing'"
          :admin-mode="adminMode"
          :admin-terms="adminTerms"
          :current-admin-term="currentAdminTerm"
          :fetch-feed="fetchFeed"
          :is-fetching="isFetching"
          :set-admin-acting-as="setAdminActingAs"
          :set-admin-by-section-ids="setAdminBySectionIds"
          :set-admin-mode="setAdminMode"
          :show-maintenance-notice="showMaintenanceNotice"
          :switch-admin-term="switchAdminTerm"
        />
      </div>
      <div v-if="!isFetching" id="select-and-confirm">
        <div
          v-if="currentWorkflowStep === 'selecting'"
          id="page-create-course-site-selecting-step"
          class="pl-3"
          :aria-expanded="`${currentWorkflowStep === 'selecting'}`"
        >
          <SelectSectionsStep
            :courses-list="coursesList"
            :current-semester="currentSemester"
            :selected-sections-list="selectedSectionsList"
            :show-confirmation="showConfirmation"
            :switch-semester="switchSemester"
            :teaching-terms="teachingTerms"
            :update-selected="updateSelected"
          />
        </div>
        <div v-if="currentWorkflowStep === 'confirmation'" :aria-expanded="`${currentWorkflowStep === 'confirmation'}`">
          <ConfirmationStep
            :course-site-creation-promise="courseSiteCreationPromise"
            :current-semester-name="currentSemesterName"
            :go-back="showSelecting"
            :selected-sections-list="selectedSectionsList"
          />
        </div>
        <div
          v-if="currentWorkflowStep === 'processing'"
          aria-live="polite"
          role="alert"
        >
          <div class="pl-8 pr-16 py-4">
            <div class="pb-3">
              <span v-if="jobStatus === 'sendingRequest'">Sending request...</span>
              <span v-if="jobStatus === 'queued'">Request sent. Awaiting processing...</span>
              <span v-if="jobStatus === 'started'">Request received. Provisioning course site...</span>
              <span v-if="jobStatus === 'finished'">Finishing up...</span>
            </div>
            <v-progress-linear
              color="primary"
              height="10"
              indeterminate
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CanvasErrors from '@/components/bcourses/CanvasErrors'
import ConfirmationStep from '@/components/bcourses/create/ConfirmationStep'
import Context from '@/mixins/Context'
import CreateCourseSiteHeader from '@/components/bcourses/create/CreateCourseSiteHeader'
import Header1 from '@/components/utils/Header1.vue'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'
import SelectSectionsStep from '@/components/bcourses/create/SelectSectionsStep'
import {courseCreate, courseProvisionJobStatus, getCourseProvisioningMetadata, getSections} from '@/api/canvas-site'
import {each, get, includes, map, size} from 'lodash'
import {iframeParentLocation} from '@/utils'

export default {
  name: 'CreateCourseSite',
  components: {
    CanvasErrors,
    ConfirmationStep,
    CreateCourseSiteHeader,
    Header1,
    MaintenanceNotice,
    SelectSectionsStep
  },
  mixins: [Context],
  data: () => ({
    adminActingAs: undefined,
    adminBySectionIds: undefined,
    adminMode: 'actAs',
    adminTerms: [],
    backgroundJobId: undefined,
    canvasSite: undefined,
    canvasSiteId: undefined,
    course: undefined,
    coursesList: [],
    currentAdminTerm: undefined,
    currentSemester: undefined,
    currentSemesterName: undefined,
    currentWorkflowStep: undefined,
    displayError: undefined,
    errorConfig: {
      header: undefined,
      supportAction: undefined,
      supportInfo: undefined
    },
    isAdmin: undefined,
    isFetching: false,
    isTeacher: undefined,
    isUidInputMode: true,
    jobStatus: undefined,
    percentComplete: undefined,
    selectedSectionsList: undefined,
    semester: undefined,
    showMaintenanceNotice: true,
    teachingTerms: [],
    timeoutPromise: undefined
  }),
  created() {
    getCourseProvisioningMetadata().then(data => {
      this.updateMetadata(data)
      this.$ready()
    })
  },
  methods: {
    classCount(semesters) {
      let count = 0
      if (size(semesters) > 0) {
        each(semesters, semester => {
          count += semester.classes.length
        })
      }
      return count
    },
    courseSiteCreationPromise(siteName, siteAbbreviation) {
      return new Promise((resolve, reject) => {
        const onError = message => {
          this.percentComplete = 0
          this.currentWorkflowStep = null
          this.jobStatus = 'error'
          this.displayError = message
          reject()
        }
        this.currentWorkflowStep = 'processing'
        this.jobStatus = 'sendingRequest'
        this.showMaintenanceNotice = false
        this.updateSelected()
        const sectionIds = map(this.selectedSectionsList, 'id')
        if (sectionIds.length > 0) {
          const adminActingAs = this.isAdmin && this.adminMode === 'actAs' ? this.adminActingAs : null
          const adminBySectionIds = this.isAdmin && this.adminMode === 'bySectionId' ? this.adminBySectionIds : null
          const adminTermSlug = this.isAdmin && this.adminMode === 'bySectionId' ? this.currentAdminTerm : null
          courseCreate(
            adminActingAs,
            adminBySectionIds,
            adminTermSlug,
            sectionIds,
            siteAbbreviation,
            siteName,
            this.currentSemester
          ).then(
            data => {
              this.backgroundJobId = data.jobId
              this.jobStatus = data.jobStatus
              this.alertScreenReader('Started course site creation.')
              this.trackBackgroundJob()
              resolve()
            },
            () => onError('Failed to create course provisioning job.')
          )
        } else {
          onError('No section IDs were provided.')
        }
      })
    },
    fetchFeed() {
      this.displayError = null
      this.isFetching = true
      this.currentWorkflowStep = 'selecting'
      this.backgroundJobId = undefined
      this.jobStatus = undefined
      this.percentComplete = undefined
      this.showMaintenanceNotice = true
      this.selectedSectionsList = []
      this.alertScreenReader('Loading courses and sections')

      const semester = (this.adminMode === 'bySectionId' ? this.currentAdminTerm : this.currentSemester)
      getSections(
        this.adminActingAs,
        this.adminBySectionIds,
        this.adminMode,
        semester,
        this.isAdmin
      ).then(
        data => {
          this.updateMetadata(data)
          this.usersClassCount = this.classCount(data.teachingTerms)
          this.teachingTerms = data.teachingTerms
          this.fillCourseSites(data.teachingTerms)
          this.alertScreenReader('Course section loaded successfully')
          if (this.adminMode === 'bySectionId' && this.adminBySectionIds) {
            each(this.coursesList, course => {
              each(course.sections, section => {
                section.selected = includes(this.adminBySectionIds, section.id)
              })
            })
            this.updateSelected()
          }
          if (!this.isAdmin && !this.usersClassCount) {
            this.displayError = 'Sorry, you are not an admin user and you have no classes.'
          }
          this.$ready()
        },
        error => {
          this.alertScreenReader('Course section loading failed')
          this.displayError = error || 'failure'
          this.$ready()
        }
      ).finally(() => {
        this.isFetching = false
      })
    },
    fillCourseSites(semestersFeed) {
      each(semestersFeed, semester => {
        each(semester.classes, course => {
          course.allSelected = false
          course.selectToggleText = 'All'
          let hasSites = false
          let sectionIdToSites = {}
          if (hasSites) {
            course.hasSites = hasSites
            each(course.sections, section => {
              if (sectionIdToSites[section.id]) {
                section.sites = sectionIdToSites[section.id]
              }
            })
          }
        })
      })
    },
    setAdminActingAs(uid) {
      this.adminActingAs = uid
      this.adminBySectionIds = null
    },
    setAdminBySectionIds(sectionIds) {
      this.adminBySectionIds = sectionIds
      this.adminActingAs = null
    },
    setAdminMode(adminMode) {
      this.adminMode = adminMode
      this.currentWorkflowStep = undefined
    },
    showConfirmation() {
      this.updateSelected()
      this.alertScreenReader('Course site details form loaded.')
      this.currentWorkflowStep = 'confirmation'
    },
    showSelecting() {
      this.currentWorkflowStep = 'selecting'
    },
    switchAdminTerm(semester) {
      if (semester && this.currentAdminTerm !== semester.slug) {
        this.currentAdminTerm = semester.slug
        this.selectedSectionsList = []
        this.updateSelected()
        this.alertScreenReader(`Switched to ${semester.name} for Section ID input`)
      }
    },
    switchSemester(semester) {
      this.currentSemester = semester.slug
      this.coursesList = semester.classes
      this.selectedSectionsList = []
      this.currentSemesterName = semester.name
      this.alertScreenReader(`Course sections for ${semester.name} loaded`)
      this.updateSelected()
    },
    trackBackgroundJob() {
      this.exportTimer = setInterval(() => {
        courseProvisionJobStatus(this.backgroundJobId).then(
          response => {
            this.jobStatus = response.jobStatus
            if (!(includes(['started', 'queued'], this.jobStatus)) || get(response, 'jobData.courseSiteUrl')) {
              clearInterval(this.exportTimer)
              if (get(response, 'jobData.courseSiteUrl')) {
                this.alertScreenReader('Done. Loading new course site now.')
                if (this.$isInIframe) {
                  iframeParentLocation(response.jobData.courseSiteUrl)
                } else {
                  window.location.href = response.jobData.courseSiteUrl
                }
              } else {
                this.jobStatus = 'error'
                this.displayError = 'An error has occurred with your request. Please try again or contact bCourses support.'
              }
            }
          }
        ).catch(
          () => {
            this.currentWorkflowStep = null
            this.jobStatus = 'error'
            this.displayError = 'An error has occurred with your request. Please try again or contact bCourses support.'
            clearInterval(this.exportTimer)
          }
        )
      }, 4000)
    },
    updateMetadata(data) {
      this.isAdmin = data.isAdmin
      this.teachingTerms = data.teachingTerms
      if (size(this.teachingTerms) > 0) {
        this.switchSemester(this.teachingTerms[0])
      }
      this.fillCourseSites(this.teachingTerms)
      if (this.isAdmin) {
        this.adminActingAs = data.adminActingAs
        this.adminTerms = data.adminTerms
        if (size(this.adminTerms) > 0 && !this.currentAdminTerm) {
          this.switchAdminTerm(this.adminTerms[0])
        }
      } else {
        this.currentWorkflowStep = 'selecting'
      }
    },
    updateSelected() {
      this.selectedSectionsList = []
      each(this.coursesList, course => {
        each(course.sections, section => {
          if (section.selected) {
            section.courseTitle = course.title
            this.selectedSectionsList.push(section)
          }
        })
      })
    }
  }
}
</script>
