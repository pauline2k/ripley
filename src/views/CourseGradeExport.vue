<template>
  <div v-if="!isLoading" class="canvas-application page-course-grade-export">
    <div>
      appState: {{ appState }}
    </div>
    <div v-if="appState === 'error'">
      <div v-if="error" role="alert">
        <p>
          <v-icon icon="mdi-exclamation-triangle" class="text-warning" /> {{ error }}
        </p>
        <p v-if="showRetryOption"><a @click="retrySelection">Retry</a></p>
        <p v-if="contactSupport">If this is not expected, please contact <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses">bCourses support</OutboundLink> for further assistance.</p>
      </div>
    </div>

    <v-container v-if="appState === 'preselection'">
      <v-row no-gutters>
        <v-col md="12">
          <div>
            <v-icon icon="mdi-angle-left" class="icon template-back-icon mr-2" />
            <a class="template-back-link" :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/grades`" target="_top">Back to Gradebook</a>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <h1 class="page-course-grade-export-header">Before exporting your E-Grades:</h1>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <h2 class="page-course-grade-export-sub-header">1. Select a grading scheme:</h2>
          <p v-if="!noGradingStandardEnabled" class="page-course-grade-export-download-description">
            You have already set a grading scheme. You can view your grading scheme or select an alternate grading scheme in
            <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/settings#tab-details`" target="_top">Course Settings</a>.
          </p>
          <p v-if="noGradingStandardEnabled" class="page-course-grade-export-download-description">
            Set a grading scheme in
            <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/settings#tab-details`" target="_top">Course Settings</a>
            and return once completed.
          </p>
          <p class="page-course-grade-export-download-description">
            For detailed instructions, see: "<OutboundLink href="https://community.canvaslms.com/docs/DOC-26521-how-do-i-enable-a-grading-scheme-for-a-course">How do I enable a grading scheme for a course?</OutboundLink>"
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <h2 class="page-course-grade-export-sub-header">2. Post all assignment grades:</h2>
          <p class="page-course-grade-export-download-description">
            All assignment grades must be posted (published/unmuted) to ensure that your E-Grades export matches what you see in the gradebook. To confirm that all grades have been posted, review all columns in
            <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/grades`" target="_top">your gradebook</a>
            for any assignments with a crossed-out eye icon
            <span class="nowrap">
              (<img class="page-course-grade-export-image-inline" src="@/assets/images/crossed_out_eye.png" alt="Crossed-out eye icon">)
            </span>
            indicating that an assignment has unposted grades.
          </p>
          <p class="page-course-grade-export-download-description">
            To post unposted grades:
          </p>
          <ul class="page-course-grade-export-download-list">
            <li>
              Mouse over the assignment name and select the three vertical dot menu
              <span class="nowrap">(<img class="page-course-grade-export-image-inline" src="@/assets/images/three_vertical_dots.png" alt="Three vertical dots">)</span>
            </li>
            <li>Select "Post grades"</li>
            <li>Select whether you wish to post grades for "Everyone," or only "Graded" students and click "Post"</li>
          </ul>
          <p class="page-course-grade-export-download-description">
            For detailed instructions, see:
            "<OutboundLink href="https://community.canvaslms.com/docs/DOC-17330-41521116619">How do I post grades for an assignment?</OutboundLink>"
          </p>
          <p class="page-course-grade-export-download-description">
            <strong>In order to avoid errors, we suggest cross-checking final grades in the bCourses gradebook with the output CSV to confirm grades were exported as expected.</strong>
          </p>
          <p class="page-course-grade-export-download-description">
            If you have used the <OutboundLink href="https://community.canvaslms.com/t5/Instructor-Guide/How-do-I-override-a-student-s-final-grade-in-the-Gradebook/ta-p/946">Final Grade Override</OutboundLink> feature to set student grades, the override grades will be included in the export.
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <div class="text-right">
            <button
              id="cancel-button"
              type="button"
              class="canvas-button"
              aria-label="Go Back to Gradebook"
              @click="goToGradebook"
            >
              Cancel
            </button>
            <button
              id="continue-button"
              type="button"
              class="canvas-button canvas-button-primary"
              :disabled="noGradingStandardEnabled"
              @click="switchToSelection"
            >
              Continue
            </button>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <v-container v-if="appState === 'selection'">
      <v-row no-gutters aria-hidden="true">
        <v-col md="12">
          <v-icon icon="mdi-angle-left" class="template-back-icon icon mr-2" />
          <a class="template-back-link" :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/grades`" target="_top">Back to Gradebook</a>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <h1
            id="page-course-grade-export-header"
            class="page-course-grade-export-header"
            tabindex="-1"
          >
            Export E-Grades
          </h1>
        </v-col>
      </v-row>
      <v-row class="sr-only">
        <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/grades`" target="_top">Back to Gradebook</a>
      </v-row>
      <v-row v-if="officialSections.length > 1" no-gutters>
        <h2 class="page-course-grade-export-download-header">Select section</h2>
      </v-row>
      <v-row v-if="officialSections.length > 1" no-gutters>
        <v-col md="5">
          <select id="course-sections" v-model="selectedSection" class="form-input-select w-100">
            <option v-for="section in officialSections" :key="section.display_name" :value="section">
              {{ section.display_name }}
            </option>
          </select>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <h2 class="page-course-grade-export-download-header">Configure P/NP grade options</h2>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="page-course-grade-export-download-description">
            <label for="input-enable-pnp-conversion-true">
              <input
                id="input-enable-pnp-conversion-true"
                v-model="enablePnpConversion"
                class="mr-2"
                type="radio"
                name="enablePnpCoversion"
                value="true"
                @change="selectedPnpCutoffGrade = ''"
              />
              Automatically convert letter grades in the E-Grades export to the student-selected grading option. Please select the lowest passing letter grade.
            </label>
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="page-course-grade-export-download-description">
            <select
              id="select-pnp-grade-cutoff"
              v-model="selectedPnpCutoffGrade"
              class="form-input-select page-course-grade-export-select-pnp-cutoff"
              :disabled="enablePnpConversion !== 'true'"
            >
              <option value="">Select a grade</option>
              <option v-for="grade in letterGrades" :key="grade" :value="grade">
                {{ grade.replace('-', '&minus;').replace('+', '&plus;') }}
              </option>
            </select>
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="page-course-grade-export-download-description">
            <label for="input-enable-pnp-conversion-true">
              <input
                id="input-enable-pnp-conversion-false"
                v-model="enablePnpConversion"
                class="mr-2"
                type="radio"
                name="enablePnpConversion"
                value="false"
                @change="selectedPnpCutoffGrade = ''"
              />
              Do not automatically convert any letter grades to P/NP. I have applied a P/NP grading scheme to all grades in this course, or will manually adjust the grades in the E-Grades Export CSV to reflect the student-selected grading option.
            </label>
          </p>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <h2 class="page-course-grade-export-download-header">What would you like to download?</h2>
      </v-row>
      <v-row no-gutters>
        <h3 class="page-course-grade-export-download-header">Current Grades</h3>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="page-course-grade-export-download-description">
            Current grades download ignores unsubmitted assignments when calculating grades.
            Use this download when you want to excuse unsubmitted assignments.
          </p>
          <button
            id="download-current-grades-button"
            type="button"
            :disabled="enablePnpConversion !== 'false' && !selectedPnpCutoffGrade"
            class="canvas-button canvas-button-primary"
            @click="preloadGrades('current')"
          >
            Download Current Grades
          </button>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <h3 class="page-course-grade-export-download-header">Final Grades</h3>
      </v-row>
      <v-row no-gutters>
        <v-col md="5">
          <p class="page-course-grade-export-download-description">
            Final grades download counts unsubmitted assignments as zeroes when calculating grades.
            Use this download when you want to include all unsubmitted assignments as part of the grade.
          </p>
          <button
            id="download-final-grades-button"
            type="button"
            :disabled="enablePnpConversion !== 'false' && !selectedPnpCutoffGrade"
            class="canvas-button canvas-button-primary"
            @click="preloadGrades('final')"
          >
            Download Final Grades
          </button>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col md="12">
          <div class="page-course-grade-export-more-info-container">
            <p class="page-course-grade-export-more-info">
              For more information, see
              <OutboundLink href="https://berkeley.service-now.com/kb?id=kb_article_view&sysparm_article=KB0010659&sys_kb_id=8b7818e11b1837ccbc27feeccd4bcbbe">From bCourses to E-Grades</OutboundLink>
            </p>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col v-if="currentUser.canvasSiteId" md="12" class="page-course-grade-export-grade-link">
          <a :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/grades`" target="_top">Back to Gradebook</a>
        </v-col>
      </v-row>
    </v-container>

    <div aria-live="polite">
      <v-container v-if="appState === 'loading'">
        <v-row no-gutters>
          <v-col md="5">
            <h1 class="page-course-grade-export-header">Preparing E-Grades for Download</h1>
          </v-col>
        </v-row>
        <div v-if="!jobStatus" class="page-course-grade-export-notice-pending-request">
          <v-progress-circular
            class="mr-2"
            color="primary"
            indeterminate
          />
          Sending preparation request...
        </div>
        <div v-if="jobStatus === 'New'" class="page-course-grade-export-notice-pending-request">
          <v-progress-circular
            class="mr-2"
            color="primary"
            indeterminate
          />
          Preparation request sent. Awaiting processing....
        </div>
        <div v-if="jobStatus">
          <ProgressBar :percent-complete-rounded="percentCompleteRounded" />
        </div>
      </v-container>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import ProgressBar from '@/components/bcourses/shared/ProgressBar'
import {downloadGradeCsv, getExportJobStatus, getExportOptions, prepareGradesCacheJob} from '@/api/canvas-site'
import {iframeParentLocation, iframeScrollToTop, putFocusNextTick} from '@/utils'

export default {
  name: 'CourseGradeExport',
  components: {OutboundLink, ProgressBar},
  mixins: [Context],
  data: () => ({
    appState: null,
    error: null,
    backgroundJobId: null,
    contactSupport: false,
    courseUserRoles: [],
    enablePnpConversion: null,
    exportTimer: null,
    jobStatus: null,
    letterGrades: ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'],
    noGradingStandardEnabled: false,
    officialSections: [],
    percentCompleteRounded: null,
    selectedPnpCutoffGrade: '',
    selectedSection: null,
    selectedType: null,
    showRetryOption: null
  }),
  beforeUnmount() {
    clearInterval(this.exportTimer)
  },
  created() {
    if (this.currentUser.isTeaching || this.currentUser.isAdmin) {
      this.loadExportOptions().then(() => {
        this.$ready()
      })
    } else {
      this.appState = 'error'
      this.error = 'You must be a teacher in this bCourses course to export to E-Grades CSV.'
      this.$ready()
    }
  },
  methods: {
    downloadGrades() {
      const pnpCutoff = this.enablePnpConversion === 'false' ? 'ignore' : encodeURIComponent(this.selectedPnpCutoffGrade)
      downloadGradeCsv(
        this.currentUser.canvasSiteId,
        this.selectedSection.sectionId,
        this.selectedSection.term_cd,
        this.selectedSection.term_yr,
        this.selectedType,
        pnpCutoff
      )
    },
    goToGradebook() {
      const gradebookUrl = `${this.canvasRootUrl}/courses/${this.currentUser.canvasSiteId}/grades`
      if (this.$isInIframe) {
        iframeParentLocation(gradebookUrl)
      } else {
        window.location.href = gradebookUrl
      }
    },
    initializePnpCutoffGrades() {
      this.enablePnpConversion = 'true'
      this.selectedPnpCutoffGrade = ''
    },
    loadExportOptions() {
      return getExportOptions(false).then(
        data => {
          this.loadSectionTerms(data.sectionTerms)
          if (this.appState !== 'error') {
            this.loadOfficialSections(data.officialSections)
          }
          if (this.appState !== 'error') {
            this.appState = 'preselection'
            if (!data.gradingStandardEnabled) {
              this.noGradingStandardEnabled = true
            }
            this.initializePnpCutoffGrades()
          }
        },
        error => {
          this.error = error
        }
      )
    },
    loadOfficialSections(officialSections) {
      if (!officialSections || !officialSections.length) {
        this.appState = 'error'
        this.error = 'None of the sections within this course site are associated with UC Berkeley course catalog sections.'
        this.contactSupport = true
      } else {
        this.officialSections = officialSections
        this.selectedSection = officialSections[0]
      }
    },
    loadSectionTerms(sectionTerms) {
      if (!sectionTerms.length) {
        this.appState = 'error'
        this.error = 'No sections found in this course representing a currently maintained campus term.'
        this.contactSupport = true
      } else if (sectionTerms.length > 1) {
        this.appState = 'error'
        this.error = 'This course site contains sections from multiple terms. Only sections from a single term should be present.'
        this.contactSupport = true
      } else {
        this.sectionTerms = sectionTerms
      }
    },
    preloadGrades(type) {
      this.selectedType = type
      this.appState = 'loading'
      this.appfocus = true
      this.jobStatus = 'New'
      iframeScrollToTop()
      prepareGradesCacheJob(this.currentUser.canvasSiteId).then(
        data => {
          if (data.jobRequestStatus === 'Success') {
            this.backgroundJobId = data.jobId
            this.startExportJob()
          } else {
            this.appState = 'error'
            this.error = 'Grade download request failed'
            this.showRetryOption = true
            this.contactSupport = false
          }
        },
        error => {
          this.error = error
        }
      )
    },
    retrySelection() {
      this.appState = 'selection'
      this.contactSupport = false
      this.error = null
      this.showRetryOption = false
    },
    startExportJob() {
      this.exportTimer = setInterval(() => {
        getExportJobStatus(this.currentUser.canvasSiteId, this.backgroundJobId).then(
          data => {
            this.jobStatus = data.jobStatus
            this.percentCompleteRounded = Math.round(data.percentComplete * 100)
            if (this.jobStatus !== 'New' && this.jobStatus !== 'Processing') {
              this.percentCompleteRounded = null
              clearInterval(this.exportTimer)
              this.$announcer.polite('Downloading export. Export form options presented for an additional download.')
              this.switchToSelection()
              this.downloadGrades()
            }
          },
          error => {
            this.error = error
          }
        )
      }, 2000)
    },
    switchToSelection() {
      iframeScrollToTop()
      this.appState = 'selection'
      putFocusNextTick('page-course-grade-export-header')
    }
  }
}
</script>

<style scoped lang="scss">
.page-course-grade-export {
  background-color: $color-white;
  padding: 15px 25px;

  // Reset to avoid default Foundation form styling
  p {
    font-family: $body-font-family;
    font-size: 14px;
    font-weight: 300;
    margin-bottom: 10px;
  }

  .page-course-grade-export-button-link {
    font-weight: 300;
  }

  .page-course-grade-export-header {
    font-family: $body-font-family;
    font-size: 23px;
    font-weight: 400;
    padding: 12px 0 0;
  }

  .page-course-grade-export-sub-header {
    font-family: $body-font-family;
    font-size: 20px;
    font-weight: 400;
    margin: 15px 0;
  }

  .page-course-grade-export-download-button-container {
    border: $color-off-black 1px solid;
    margin: 10px;
  }

  .page-course-grade-export-download-description {
    line-height: 18px;
    margin-bottom: 10px;
    padding: 4px 0;
  }

  .page-course-grade-export-download-header {
    font-size: 20px;
    font-weight: 400;
    margin: 30px 0 5px;
  }

  .page-course-grade-export-download-list {
    line-height: 18px;
    list-style-position: inside;
    list-style-type: disc;
    margin-bottom: 10px;
    padding: 4px 0;
  }

  .page-course-grade-export-image-inline {
    height: 20px;
  }

  .page-course-grade-export-more-info-container {
    margin-top: 40px;
  }

  .page-course-grade-export-more-info {
    margin: 20px 0;
  }

  .page-course-grade-export-section {
    margin: 10px 0;
  }

  .page-course-grade-export-form-label {
    display: inline-block;
    margin: 8px 0;
  }

  .page-course-grade-export-notice-pending-request {
    margin: 15px auto;
  }

  .page-course-grade-export-refresh-button {
    font-size: 11px;
    padding: 1px 5px;
    text-decoration: none;
  }

  .page-course-grade-export-select-pnp-cutoff {
    padding-right: 25px;
    width: fit-content;
  }
}
</style>
