<template>
  <div class="canvas-application page-site-mailing-list">
    <h1 class="header header1">Manage a Site Mailing List</h1>
    <div v-if="alerts.error.length" role="alert" class="alert alert-error">
      <v-icon icon="mdi-exclamation-triangle" class="icon left icon-red canvas-notice-icon" />
      <div class="ml-3">
        <div v-for="error in alerts.error" :key="error">{{ error }}</div>
      </div>
    </div>

    <div v-if="alerts.success.length" role="alert" class="alert alert-success">
      <v-icon icon="mdi-check-circle" class="icon left icon-green canvas-notice-icon" />
      <div class="ml-3">
        <div v-for="success in alerts.success" :key="success">{{ success }}</div>
      </div>
    </div>

    <div v-if="listCreated && !mailingList.timeLastPopulated" role="alert" class="alert alert-info">
      The list <strong>"{{ mailingList.name }}@{{ mailingList.domain }}"</strong> has been created. Choose "Update membership from course site" to add members.
    </div>

    <div v-if="siteSelected && !listCreated" role="alert" class="alert alert-info">
      No mailing list has been created for this site.
    </div>

    <div v-if="!siteSelected" class="align-center d-flex flex-wrap pa-3">
      <div class="pr-2">
        <label for="page-site-mailing-list-site-id" class="sr-only">Course Site ID</label>
        <v-text-field
          id="page-site-mailing-list-site-id"
          v-model="canvasSite.canvasCourseId"
          aria-required="true"
          :error="!!$_.trim(canvasSite.canvasCourseId) && !isCanvasCourseIdValid"
          hide-details
          maxlength="9"
          label="Canvas Course ID"
          required
          style="width: 200px"
          @keydown.enter="findSiteMailingList"
        />
      </div>
      <div>
        <v-btn
          id="btn-get-mailing-list"
          :disabled="isProcessing || !isCanvasCourseIdValid"
          size="large"
          @click="findSiteMailingList"
        >
          <span v-if="!isProcessing">Get Mailing List</span>
          <span v-if="isProcessing">
            <v-progress-circular
              class="mr-2"
              color="primary"
              indeterminate
              size="x-small"
            />
            Searching...
          </span>
        </v-btn>
      </div>
    </div>

    <div v-if="siteSelected">
      <div id="mailing-list-details" class="page-site-mailing-list-info-box">
        <h2 id="mailing-list-details-header" class="header page-site-mailing-list-header2" tabindex="-1">
          <span v-if="!listCreated" class="ellipsis">{{ canvasSite.name }}</span>
          <span v-if="listCreated" class="ellipsis">{{ mailingList.name }}@{{ mailingList.domain }}</span>
        </h2>
        <div v-if="listCreated">
          <div id="mailing-list-member-count">{{ pluralize('member', mailingList.membersCount, {0: 'No'}) }}</div>
          <div>Membership last updated: <strong id="mailing-list-membership-last-updated">{{ listLastPopulated }}</strong></div>
          <div>
            Course site:
            <OutboundLink
              id="mailing-list-court-site-name"
              :href="canvasSite.url"
              @click="trackExternalLink('Canvas Site Mailing List', 'bCourses', canvasSite.url)"
            >
              {{ canvasSite.name }}
            </OutboundLink>
          </div>
        </div>
        <v-row no-gutters>
          <v-col id="mailing-list-canvas-code-and-term" sm="12" md="4">{{ canvasSite.codeAndTerm }}</v-col>
          <v-col id="mailing-list-canvas-course-id" sm="12" md="6">Site ID: {{ canvasSite.canvasCourseId }}</v-col>
        </v-row>
        <OutboundLink
          v-if="!listCreated"
          id="view-course-site-link"
          :href="canvasSite.url"
          @click="trackExternalLink('Canvas Site Mailing List', 'bCourses', canvasSite.url)"
        >
          View course site
        </OutboundLink>
      </div>

      <form class="canvas-page-form canvas-form">
        <div v-if="!listCreated">
          <v-row no-gutters class="page-site-mailing-list-form-input-row">
            <v-col sm="12" md="3">
              <label for="mailingListName" class="page-site-mailing-list-form-label">New Mailing List Name:</label>
            </v-col>
            <v-col sm="12" md="9">
              <v-text-field
                id="mailingListName"
                v-model="mailingList.name"
                aria-required="true"
                hide-details
                required
              />
            </v-col>
          </v-row>
        </div>

        <div class="form-actions">
          <v-btn
            v-if="!listCreated"
            id="btn-create-mailing-list"
            aria-controls="page-reader-alert"
            @click="registerMailingList"
          >
            <span>Create mailing list</span>
          </v-btn>
          <v-btn
            v-if="listCreated"
            id="btn-populate-mailing-list"
            aria-controls="page-reader-alert"
            @click="populateMailingList"
          >
            <span v-if="!isProcessing">Update membership from course site</span>
            <span v-if="isProcessing">
              <v-progress-circular
                class="mr-2"
                color="primary"
                indeterminate
              />
              Updating...
            </span>
          </v-btn>
          <v-btn id="btn-cancel" @click="resetForm">
            Cancel
          </v-btn>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import Utils from '@/mixins/Utils'
import {createSiteMailingListAdmin, getSiteMailingListAdmin, populateSiteMailingList} from '@/api/mailing-lists'

export default {
  name: 'SiteMailingLists',
  components: {OutboundLink},
  mixins: [Context, Utils],
  data: () => ({
    alerts: {
      error: [],
      success: []
    },
    canvasSite: {},
    isProcessing: false,
    listCreated: false,
    listLastPopulated: null,
    mailingList: {},
    siteSelected: false
  }),
  computed: {
    isCanvasCourseIdValid() {
      const canvasCourseId = this.$_.trim(this.canvasSite.canvasCourseId)
      return !!canvasCourseId && canvasCourseId.match(/^\d+$/)
    }
  },
  mounted() {
    this.$ready()
  },
  methods: {
    findSiteMailingList() {
      if (!this.isProcessing && this.canvasSite.canvasCourseId) {
        this.isProcessing = true
        getSiteMailingListAdmin(this.canvasSite.canvasCourseId).then(this.updateDisplay, this.$errorHandler)
      }
    },
    populateMailingList() {
      this.$announcer.polite('Updating membership')
      this.isProcessing = true
      populateSiteMailingList(this.canvasSite.canvasCourseId).then(data => {
        this.updateDisplay(data)
        if (!data || !data.populationResults) {
          this.alerts.error.push('The mailing list could not be populated.')
        }
      })
    },
    registerMailingList() {
      this.$announcer.polite('Creating list')
      this.isProcessing = true
      createSiteMailingListAdmin(this.canvasSite.canvasCourseId, this.mailingList).then(this.updateDisplay, this.$errorHandler)
    },
    resetForm() {
      this.canvasSite = {}
      this.mailingList = {}
      this.updateDisplay({})
      this.$announcer.polite('Canceled.')
      this.$putFocusNextTick('page-site-mailing-list-site-id')
    },
    trackExternalLink() {
      // TODO implement CLC-7512
    },
    updateCodeAndTerm(canvasSite) {
      const codeAndTermArray = []
      if (canvasSite.courseCode !== canvasSite.name) {
        codeAndTermArray.push(canvasSite.courseCode)
      }
      if (canvasSite.term && canvasSite.term.name) {
        codeAndTermArray.push(canvasSite.term.name)
      }
      canvasSite.codeAndTerm = codeAndTermArray.join(', ')
    },
    updateDisplay(data) {
      if (data) {
        this.alerts.success = []
        this.alerts.error = data.errorMessages || []
        this.canvasSite = data.canvasSite || {}
        this.mailingList = data.mailingList || {}
        this.siteSelected = !!this.$_.get(data, 'canvasSite.canvasCourseId')
        this.listCreated = (this.$_.get(data, 'mailingList.state') === 'created')
        if (this.siteSelected) {
          this.updateCodeAndTerm(this.canvasSite)
          this.$putFocusNextTick('mailing-list-details-header')
        }
        if (this.listCreated) {
          this.updateListLastPopulated(this.mailingList)
        }
        if (data.populationResults) {
          this.updatePopulationResults(data.populationResults)
        }
        this.isProcessing = false
      } else {
        this.alerts.error = [`bCourses site ${this.canvasSite.canvasCourseId} has no mailing list.`]
      }
    },
    updateListLastPopulated(mailingList) {
      if (mailingList.timeLastPopulated) {
        this.listLastPopulated = this.$moment.unix(mailingList.timeLastPopulated.epoch).format('MMM D, YYYY')
      } else {
        this.listLastPopulated = 'never'
      }
    },
    updatePopulationResults(populationResults) {
      if (populationResults.success) {
        this.alerts.success.push('Memberships were successfully updated.')
        if (populationResults.messages.length) {
          this.alerts.success = this.alerts.success.concat(populationResults.messages)
        } else {
          this.alerts.success.push('No changes in membership were found.')
        }
      } else {
        this.alerts.error.push('There were errors during the last membership update.')
        this.alerts.error = this.alerts.error.concat(populationResults.messages)
        this.alerts.error.push('You can attempt to correct the errors by running the update again.')
      }
    }
  }
}
</script>

<style scoped lang="scss">
.page-site-mailing-list {
  padding: 20px;

  .page-site-mailing-list-button-primary {
    margin: 0 4px;
  }

  .page-site-mailing-list-header2 {
    font-size: 17px;
    line-height: 25px;
  }

  .page-site-mailing-list-header3 {
    font-size: 15px;
    line-height: 22px;
  }

  .page-site-mailing-list-info-box {
    border: 1px solid $color-container-grey-border;
    margin: 24px 0;
    padding: 6px 10px;
  }

  .page-site-mailing-list-form {
    margin: 20px 0;
  }

  .page-site-mailing-list-form-input-row {
    margin: 20px 0;
    text-align: right;
  }

  .page-site-mailing-list-form-label {
    text-align: right;
  }

  .page-site-mailing-list-form-label-long {
    display: inline;
    font-weight: 300;
    text-align: left;
  }

  .page-site-mailing-list-text {
    font-size: 14px;
    font-weight: 300;
    line-height: 1.6;
    margin: 15px;
  }

  @media #{$small-only} {
    .page-site-mailing-list-form-label {
      text-align: left;
    }
  }
}
</style>
