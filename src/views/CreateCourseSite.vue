<template>
  <div class="pb-5 px-5">
    <Header1 class="mb-2" text="Create a Course Site" />
    <v-alert
      v-if="warning"
      id="canvas-error-container"
      class="mb-3"
      density="compact"
      role="alert"
      type="warning"
    >
      {{ warning }}
    </v-alert>
    <div v-if="!isLoading">
      <div v-if="isAdmin && currentWorkflowStep !== 'processing'" class="pl-3">
        <CreateCourseSiteHeader
          :admin-mode="adminMode"
          :admin-terms="adminTerms"
          :current-admin-term="currentAdminTerm"
          :fetch-feed="fetchFeed"
          :is-fetching="isFetching"
          :set-admin-acting-as="setAdminActingAs"
          :set-admin-by-section-ids="setAdminBySectionIds"
          :set-admin-mode="setAdminMode"
          :set-warning="w => warning = w"
          :switch-admin-term="switchAdminTerm"
        />
      </div>
      <div v-if="!isFetching" :class="{'pt-2': isAdmin && currentWorkflowStep !== 'processing'}">
        <SelectSectionsStep
          v-if="currentWorkflowStep === 'selecting'"
          :admin-acting-as="adminActingAs"
          :courses-list="coursesList"
          :current-semester="currentSemester"
          :selected-sections-list="selectedSectionsList"
          :show-confirmation="showConfirmation"
          :switch-semester="switchSemester"
          :teaching-terms="teachingTerms"
          :update-selected="updateSelected"
        />
        <div v-if="currentWorkflowStep === 'confirmation'">
          <ConfirmationStep
            :course-site-creation-promise="courseSiteCreationPromise"
            :current-semester-name="currentSemesterName"
            :go-back="onCancelConfirmationStep"
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
import ConfirmationStep from '@/components/bcourses/create/ConfirmationStep'
import Context from '@/mixins/Context'
import CreateCourseSiteHeader from '@/components/bcourses/create/CreateCourseSiteHeader'
import Header1 from '@/components/utils/Header1'
import SelectSectionsStep from '@/components/bcourses/create/SelectSectionsStep'
import {courseCreate, courseProvisionJobStatus, getCourseProvisioningMetadata, getSections} from '@/api/canvas-site'
import {each, find, get, includes, map, size} from 'lodash'
import {iframeParentLocation, putFocusNextTick} from '@/utils'

export default {
  name: 'CreateCourseSite',
  components: {
    ConfirmationStep,
    CreateCourseSiteHeader,
    Header1,
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
    teachingTerms: [],
    timeoutPromise: undefined,
    warning: undefined
  }),
  created() {
    getCourseProvisioningMetadata().then(data => {
      this.updateMetadata(data)
      if (!this.teachingTerms.length && !this.currentUser.isAdmin) {
        this.warning = 'You are not listed as an instructor of any courses in the current or upcoming term.'
      }
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
          this.warning = message
          putFocusNextTick('page-title')
          reject()
        }
        this.currentWorkflowStep = 'processing'
        this.jobStatus = 'sendingRequest'
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
      this.warning = null
      this.isFetching = true
      this.currentWorkflowStep = 'selecting'
      this.backgroundJobId = undefined
      this.jobStatus = undefined
      this.percentComplete = undefined
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
          if (!this.teachingTerms.length && this.adminMode) {
            this.warning = this.adminActingAs ? `UID ${this.adminActingAs} is not listed as an instructor of any courses in the current or upcoming term.` : 'No matching courses found.'
          }
          this.fillCourseSites(this.teachingTerms)
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
            this.warning = 'Sorry, you are not an admin user and you have no classes.'
          }
        },
        error => {
          this.alertScreenReader('Course section loading failed')
          this.warning = error || 'failure'
        }
      ).finally(() => {
        this.isFetching = false
        putFocusNextTick(this.adminMode === 'bySectionId' ? 'sections-by-ids-button' : 'sections-by-uid-button')
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
    onCancelConfirmationStep() {
      this.currentWorkflowStep = 'selecting'
    },
    switchAdminTerm(semester) {
      if (semester && this.currentAdminTerm !== semester.slug) {
        this.currentWorkflowStep = null
        this.currentAdminTerm = semester.slug
        this.selectedSectionsList = []
        this.updateSelected()
        this.alertScreenReader(`Switched to ${semester.name} for Section ID input`)
      }
    },
    switchSemester(slug) {
      const teachingTerm = find(this.teachingTerms, t => t.slug === slug)
      const term = teachingTerm || find(this.adminTerms, t => t.slug === slug)
      this.coursesList = teachingTerm ? teachingTerm.classes : []
      this.currentSemester = slug
      this.currentSemesterName = term.name
      this.selectedSectionsList = []
      this.alertScreenReader(`Course sections for ${term.name} loaded`)
      this.updateSelected()
    },
    trackBackgroundJob() {
      this.exportTimer = setInterval(() => {
        courseProvisionJobStatus(this.backgroundJobId).then(
          response => {
            if (response.jobStatus !== this.jobStatus) {
              this.jobStatus = response.jobStatus
            } else {
              this.alertScreenReader(`Still ${includes(['sendingRequest', 'queued'], this.jobStatus) ? 'waiting' : 'processing'}`)
            }
            if (!(includes(['started', 'queued'], this.jobStatus)) || get(response, 'jobData.courseSiteUrl')) {
              clearInterval(this.exportTimer)
              if (get(response, 'jobData.courseSiteUrl')) {
                this.alertScreenReader('Done. Loading new course site.')
                if (this.$isInIframe) {
                  iframeParentLocation(response.jobData.courseSiteUrl)
                } else {
                  window.location.href = response.jobData.courseSiteUrl
                }
              } else {
                this.alertScreenReader('Error.', 'assertive')
                this.jobStatus = 'error'
                this.warning = 'An error has occurred with your request. Please try again or contact bCourses support.'
                putFocusNextTick('page-title')
              }
            }
          }
        ).catch(
          () => {
            this.alertScreenReader('Error.', 'assertive')
            this.currentWorkflowStep = null
            this.jobStatus = 'error'
            this.warning = 'An error has occurred with your request. Please try again or contact bCourses support.'
            clearInterval(this.exportTimer)
            putFocusNextTick('page-title')
          }
        )
      }, 4000)
    },
    updateMetadata(data) {
      this.isAdmin = data.isAdmin
      this.teachingTerms = data.teachingTerms
      if (size(this.teachingTerms) > 0) {
        this.switchSemester(this.teachingTerms[0].slug)
      }
      this.fillCourseSites(this.teachingTerms)
      if (this.isAdmin) {
        this.adminActingAs = data.adminActingAs
        this.adminTerms = data.adminTerms
        if (size(this.teachingTerms) > 0 && this.adminTerms.length) {
          this.switchSemester(this.teachingTerms[0].slug)
        }
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
