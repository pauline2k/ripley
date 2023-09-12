<template>
  <div class="page-create-course-site pl-5 pr-5 pt-3 pb-3">
    <div v-if="!isLoading && !displayError" class="accessibility-no-outline">
      <div class="d-flex flex-column pt-3">
        <div>
          <div v-if="showMaintenanceNotice" role="alert">
            <MaintenanceNotice course-action-verb="site is created" />
          </div>
        </div>
        <div>
          <h1 class="page-create-course-site-header page-create-course-site-header1">Create a Course Site</h1>
        </div>
        <div>
          <CreateCourseSiteHeader
            v-if="isAdmin && currentWorkflowStep !== 'monitoringJob'"
            :admin-mode="adminMode"
            :admin-terms="adminTerms"
            :current-admin-term="currentAdminTerm"
            :fetch-feed="fetchFeed"
            :set-admin-acting-as="setAdminActingAs"
            :set-admin-by-section-ids="setAdminBySectionIds"
            :set-admin-mode="setAdminMode"
            :show-maintenance-notice="showMaintenanceNotice"
            :switch-admin-term="switchAdminTerm"
          />
        </div>
      </div>
      <div v-if="isAdmin && !currentWorkflowStep">
        Use inputs above to choose courses by Section ID or as an instructor.
      </div>
      <div id="page-create-course-site-steps-container" class="p-0">
        <div
          v-if="currentWorkflowStep === 'selecting'"
          id="page-create-course-site-selecting-step"
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
        <div
          v-if="currentWorkflowStep === 'confirmation'"
          id="page-create-course-site-confirmation-step"
          :aria-expanded="`${currentWorkflowStep === 'confirmation'}`"
        >
          <ConfirmationStep
            :start-course-site-job="startCourseSiteJob"
            :current-semester-name="currentSemesterName"
            :go-back="showSelecting"
            :selected-sections-list="selectedSectionsList"
          />
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
              Request received. Provisioning course site...
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
    </div>
    <div v-if="displayError" class="pt-5">
      <CanvasErrors :message="displayError" />
    </div>
  </div>
</template>

<script>
import CanvasErrors from '@/components/bcourses/CanvasErrors'
import ConfirmationStep from '@/components/bcourses/create/ConfirmationStep'
import Context from '@/mixins/Context'
import CreateCourseSiteHeader from '@/components/bcourses/create/CreateCourseSiteHeader'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'
import SelectSectionsStep from '@/components/bcourses/create/SelectSectionsStep'
import {courseCreate, courseProvisionJobStatus, getCourseProvisioningMetadata, getSections} from '@/api/canvas-site'
import {each, get, includes, map, size} from 'lodash'
import {iframeParentLocation} from '@/utils'

export default {
  name: 'CreateCourseSite',
  mixins: [Context],
  components: {
    CanvasErrors,
    ConfirmationStep,
    CreateCourseSiteHeader,
    MaintenanceNotice,
    SelectSectionsStep
  },
  data: () => ({
    adminActingAs: undefined,
    adminBySectionIds: undefined,
    adminMode: 'actAs',
    adminTerms: [],
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
      this.$ready('Create Canvas Course Site')
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
    clearCourseSiteJob() {
      this.jobId = undefined
      this.jobStatus = undefined
      this.completedSteps = undefined
      this.percentComplete = undefined
      this.showMaintenanceNotice = true
    },
    fetchFeed() {
      this.clearCourseSiteJob()
      this.currentWorkflowStep = 'selecting'
      this.selectedSectionsList = []
      this.$announcer.polite('Loading courses and sections')

      const onSuccess = data => {
        this.updateMetadata(data)
        this.usersClassCount = this.classCount(data.teachingTerms)
        this.teachingTerms = data.teachingTerms
        this.canvasSite = data.canvas_site
        const canvasSiteId = this.canvasSite ? this.canvasSite.canvasSiteId : ''
        this.fillCourseSites(data.teachingTerms, canvasSiteId)
        this.$announcer.polite('Course section loaded successfully')
        if (this.adminMode === 'bySectionId' && this.adminBySectionIds) {
          each(this.coursesList, course => {
            each(course.sections, section => {
              section.selected = includes(this.adminBySectionIds, section.sectionId)
            })
          })
          this.updateSelected()
        }
        if (!this.isAdmin && !this.usersClassCount) {
          this.displayError = 'Sorry, you are not an admin user and you have no classes.'
        }
        this.$ready()
      }

      const onError = () => {
        this.$announcer.polite('Course section loading failed')
        this.displayError = 'failure'
        this.$ready()
      }

      const semester = (this.adminMode === 'bySectionId' ? this.currentAdminTerm : this.currentSemester)

      getSections(
        this.adminActingAs,
        this.adminBySectionIds,
        this.adminMode,
        semester,
        this.isAdmin
      ).then(onSuccess, onError)
    },
    fillCourseSites(semestersFeed, canvasSiteId=null) {
      each(semestersFeed, semester => {
        each(semester.classes, course => {
          course.allSelected = false
          course.selectToggleText = 'All'
          let hasSites = false
          let sectionIdToSites = {}
          each(course.class_sites, site => {
            if (site.emitter === 'bCourses') {
              if (site.id !== canvasSiteId) {
                each(site.sections, siteSection => {
                  hasSites = true
                  if (!sectionIdToSites[siteSection.sectionId]) {
                    sectionIdToSites[siteSection.sectionId] = []
                  }
                  sectionIdToSites[siteSection.sectionId].push(site)
                })
              }
            }
          })
          if (hasSites) {
            course.hasSites = hasSites
            each(course.sections, section => {
              let sectionId = section.sectionId
              if (sectionIdToSites[sectionId]) {
                section.sites = sectionIdToSites[sectionId]
              }
            })
          }
        })
      })
    },
    loadCourseLists() {
      this.courseSemester = false
      // identify semester matching current course site
      each(this.teachingTerms, term => {
        if ((term.termYear === this.canvasSite.term.term_yr) && (term.termCode === this.canvasSite.term.term_cd)) {
          this.courseSemester = semester
          return false
        }
      })
      if (this.courseSemester) {
        // count classes only in course semester to determine authorization to use this tool
        this.usersClassCount = this.courseSemester.classes.length

        // generate list of existing course sections for preview table
        // and flattened array of all sections for current sections staging table
        this.existingCourseSections = []
        this.allSections = []
        const existingSectionIds = []
        each(this.courseSemester.classes, classItem => {
          each(classItem.sections, section => {
            section.parentClass = classItem
            this.allSections.push(section)
            section.stagedState = null
            each(this.canvasSite.officialSections, officialSection => {
              if (officialSection.sectionId === section.sectionId && existingSectionIds.indexOf(section.sectionId) === -1) {
                existingSectionIds.push(section.sectionId)
                this.existingCourseSections.push(section)
                if (officialSection.name !== `${section.courseCode} ${section.section_label}`) {
                  section.nameDiscrepancy = true
                }
              }
            })
          })
        })
      } else {
        this.usersClassCount = 0
      }
    },
    selectedSections(coursesList) {
      const selected = []
      each(coursesList, course => {
        each(course.sections, section => {
          if (section.selected) {
            section.courseTitle = course.title
            section.courseCatalog = course.course_catalog
            selected.push(section)
          }
        })
      })
      return selected
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
      this.$announcer.polite('Course site details form loaded.')
      this.currentWorkflowStep = 'confirmation'
    },
    showSelecting() {
      this.currentWorkflowStep = 'selecting'
    },
    startCourseSiteJob(siteName, siteAbbreviation) {
      this.currentWorkflowStep = 'processing'
      this.jobStatus = 'sendingRequest'
      this.showMaintenanceNotice = false
      this.updateSelected()
      const sectionIds = map(this.selectedSectionsList, 'id')
      if (sectionIds.length > 0) {
        const onSuccess = data => {
          this.jobId = data.jobId
          this.jobStatus = data.jobStatus
          this.$announcer.polite('Started course site creation.')
          this.completedFocus = true
          this.trackBackgroundJob()
        }
        const onError = () => {
          this.percentComplete = 0
          this.currentWorkflowStep = null
          this.jobStatus = 'error'
          this.displayError = 'Failed to create course provisioning job.'
        }
        courseCreate(
          this.isAdmin && this.adminMode === 'actAs' ? this.adminActingAs : null,
          this.isAdmin && this.adminMode === 'bySectionId' ? this.adminBySectionIds : null,
          this.isAdmin && this.adminMode === 'bySectionId' ? this.currentAdminTerm : null,
          sectionIds,
          siteAbbreviation,
          siteName,
          this.currentSemester
        ).then(onSuccess, onError)
      }
    },
    switchAdminTerm(semester) {
      this.currentAdminTerm = semester.slug
      this.selectedSectionsList = []
      this.updateSelected()
      this.$announcer.polite(`Switched to ${semester.name} for Section ID input`)
    },
    switchSemester(semester) {
      this.currentSemester = semester.slug
      this.coursesList = semester.classes
      this.selectedSectionsList = []
      this.currentSemesterName = semester.name
      this.$announcer.polite(`Course sections for ${semester.name} loaded`)
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
                this.$announcer.polite('Done. Loading new course site now.')
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
      this.selectedSectionsList = this.selectedSections(this.coursesList)
    }
  }
}
</script>

<style scoped lang="scss">
.page-create-course-site {
  padding: 25px;

  .button {
    padding: 10px;
  }
  .page-button-grey {
    background: linear-gradient($color-button-grey-gradient-1, $color-button-grey-gradient-2);
    border: 1px solid $color-button-grey-border;
    color: $color-button-grey-text;
  }
  .page-create-course-site-choices {
    overflow: hidden;
    li {
      border-left: 1px solid $color-very-light-grey;
      float: left;
      max-width: 250px;
      padding: 15px;
      width: 50%;
      &:first-child {
        border: 0;
      }
    }
  }
  .page-create-course-site-form-course-button {
    color: $color-body-black;

    &:focus, &:hover {
      text-decoration: none;
    }
  }
  .page-create-course-site-header {
    color: $color-headers;
    font-family: $body-font-family;
    font-weight: normal;
    line-height: 40px;
    margin: 5px 0;
  }
  .page-create-course-site-header1 {
    font-size: 23px;
  }
}
</style>
