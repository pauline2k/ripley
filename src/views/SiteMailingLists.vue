<template>
  <div class="canvas-application page-site-mailing-list">
    <h1 id="page-header" tabindex="-1">Manage a Site Mailing List</h1>
    <v-alert
      v-if="errorMessages.length"
      class="mb-2"
      closable
      density="compact"
      role="alert"
      type="warning"
    >
      <div v-for="error in errorMessages" :key="error">{{ error }}</div>
    </v-alert>

    <v-alert
      v-if="successMessages.length"
      class="mb-2"
      closable
      density="compact"
      role="alert"
      type="success"
    >
      <div v-for="success in successMessages" :key="success">{{ success }}</div>
    </v-alert>

    <v-alert
      v-if="listCreated && !mailingList.timeLastPopulated"
      class="mb-2"
      color="primary"
      closable
      density="compact"
      role="alert"
      type="info"
    >
      The list <strong>"{{ mailingList.name }}{{ mailingList.domain ? `@${mailingList.domain}` : '' }}"</strong> exists.
      Choose "Update membership from course site" to add members.
    </v-alert>

    <v-alert
      v-if="siteSelected && !listCreated"
      class="mb-2"
      closable
      color="primary"
      density="compact"
      role="alert"
      type="info"
    >
      No mailing list has been created for this site.
    </v-alert>

    <div v-if="!siteSelected" class="align-center d-flex flex-wrap pa-3">
      <div class="pr-3">
        <label for="page-site-mailing-list-site-id" class="sr-only">Course Site ID</label>
        <v-text-field
          id="page-site-mailing-list-site-id"
          v-model="modelCanvasCourseId"
          aria-required="true"
          :error="!!$_.trim(modelCanvasCourseId) && !isCanvasCourseIdValid(modelCanvasCourseId)"
          hide-details
          maxlength="10"
          label="Canvas Course ID"
          required
          style="width: 200px"
          variant="outlined"
          @keydown.enter="findSiteMailingList"
        />
      </div>
      <div>
        <v-btn
          id="btn-get-mailing-list"
          color="primary"
          :disabled="isProcessing || !isCanvasCourseIdValid(modelCanvasCourseId)"
          @click="findSiteMailingList"
        >
          <span v-if="!isProcessing">Get Mailing List</span>
          <span v-if="isProcessing">
            <SpinnerWithinButton /> Searching...
          </span>
        </v-btn>
      </div>
    </div>

    <div v-if="siteSelected" class="mt-4">
      <v-card id="mailing-list-details">
        <v-card-text>
          <h2 id="mailing-list-details-header" class="page-site-mailing-list-header2" tabindex="-1">
            <span v-if="!listCreated" class="ellipsis">{{ canvasSite.name }}</span>
            <span v-if="listCreated" class="ellipsis">{{ mailingList.name }}@{{ mailingList.domain }}</span>
          </h2>
          <div v-if="listCreated" class="pt-2">
            <div id="mailing-list-member-count">{{ pluralize('member', mailingList.membersCount, {0: 'No'}) }}</div>
            <div>Membership last updated: <strong id="mailing-list-membership-last-updated">{{ listLastPopulated }}</strong></div>
            <div class="pt-2">
              Course site:
              <OutboundLink
                id="mailing-list-court-site-name"
                :href="canvasSite.url"
              >
                {{ canvasSite.name }}
              </OutboundLink>
            </div>
          </div>
          <div class="d-flex flex-wrap justify-space-between mb-2">
            <div id="mailing-list-canvas-code-and-term">{{ canvasSite.codeAndTerm }}</div>
            <div id="mailing-list-canvas-course-id">
              <span class="font-weight-medium">Site ID:</span>
              {{ canvasSite.canvasCourseId }}
            </div>
          </div>
        </v-card-text>
        <v-card-actions v-if="!listCreated">
          <OutboundLink
            id="view-course-site-link"
            class="mb-3 px-3"
            :href="canvasSite.url"
          >
            View course site
          </OutboundLink>
        </v-card-actions>
      </v-card>

      <div v-if="!listCreated" class="py-8">
        <h2>Create Mailing List</h2>
        <div class="align-center d-flex flex-wrap pt-2">
          <div class="pr-3">
            <label for="mailing-list-name-input">Name:</label>
          </div>
          <div class="w-75">
            <v-text-field
              id="mailing-list-name-input"
              v-model="mailingList.name"
              aria-required="true"
              hide-details
              maxlength="255"
              variant="outlined"
              required
              @keydown.enter="registerMailingList"
            />
          </div>
        </div>
      </div>

      <div class="d-flex justify-end mt-4">
        <v-btn
          id="btn-cancel"
          class="mr-1"
          variant="text"
          @click="resetForm"
        >
          Cancel
        </v-btn>
        <v-btn
          v-if="!listCreated"
          id="btn-create-mailing-list"
          color="primary"
          :disabled="isProcessing || !$_.trim(mailingList.name)"
          @click="registerMailingList"
        >
          <span v-if="!isProcessing">Create mailing list</span>
          <span v-if="isProcessing">
            <SpinnerWithinButton /> Creating...
          </span>
        </v-btn>
        <v-btn
          v-if="listCreated"
          id="btn-populate-mailing-list"
          color="primary"
          @click="populateMailingList"
        >
          <span v-if="!isProcessing">Update membership from course site</span>
          <span v-if="isProcessing">
            <SpinnerWithinButton /> Updating...
          </span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import CanvasUtils from '@/mixins/CanvasUtils.vue'
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import Utils from '@/mixins/Utils'
import {createSiteMailingListAdmin, getSiteMailingListAdmin, populateSiteMailingList} from '@/api/mailing-lists'

export default {
  name: 'SiteMailingLists',
  components: {OutboundLink, SpinnerWithinButton},
  mixins: [CanvasUtils, Context, Utils],
  data: () => ({
    errorMessages: [],
    isProcessing: false,
    listLastPopulated: null,
    mailingList: undefined,
    modelCanvasCourseId: undefined,
    successMessages: []
  }),
  computed: {
    canvasCourseId() {
      return this.$_.get(this.canvasSite, 'canvasCourseId')
    },
    canvasSite() {
      return this.$_.get(this.mailingList, 'canvasSite')
    },
    listCreated() {
      return this.$_.get(this.mailingList, 'state') === 'created'
    },
    siteSelected() {
      return !!this.$_.get(this.canvasSite, 'canvasCourseId')
    }
  },
  mounted() {
    this.$putFocusNextTick('page-header')
    this.$ready()
  },
  methods: {
    axiosErrorHandler(message) {
      this.errorMessages = [message]
      this.isProcessing = false
    },
    clearAlerts() {
      this.errorMessages = this.successMessages = []
    },
    findSiteMailingList() {
      if (!this.isProcessing && this.modelCanvasCourseId) {
        this.isProcessing = true
        getSiteMailingListAdmin(this.modelCanvasCourseId).then(
          this.updateDisplay,
          this.axiosErrorHandler
        )
      }
    },
    populateMailingList() {
      this.clearAlerts()
      this.$announcer.polite('Updating membership')
      this.isProcessing = true
      populateSiteMailingList(this.canvasCourseId).then(
        data => {
          this.updateDisplay(data)
          if (!data || !data.populationResults) {
            this.errorMessages.push('The mailing list could not be populated.')
          }
        },
        this.axiosErrorHandler
      )
    },
    registerMailingList() {
      this.clearAlerts()
      this.$announcer.polite('Creating list')
      this.isProcessing = true
      const name = this.$_.trim(this.mailingList.name)
      if (name) {
        createSiteMailingListAdmin(this.canvasCourseId, name).then(this.updateDisplay, this.axiosErrorHandler)
      }
    },
    resetForm() {
      this.mailingList = undefined
      this.modelCanvasCourseId = undefined
      this.$announcer.polite('Canceled.')
      this.$putFocusNextTick('page-site-mailing-list-site-id')
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
      this.mailingList = data
      this.successMessages = []
      this.errorMessages = this.mailingList.errorMessages || []
      if (this.siteSelected) {
        this.updateCodeAndTerm(this.canvasSite)
        this.$putFocusNextTick('mailing-list-details-header')
      }
      if (this.listCreated) {
        this.updateListLastPopulated()
      }
      if (this.mailingList.populationResults) {
        this.updatePopulationResults(this.mailingList.populationResults)
      }
      this.isProcessing = false
    },
    updateListLastPopulated() {
      if (this.mailingList && this.mailingList.timeLastPopulated) {
        this.listLastPopulated = this.$moment.unix(this.mailingList.timeLastPopulated.epoch).format('MMM D, YYYY')
      } else {
        this.listLastPopulated = 'never'
      }
    },
    updatePopulationResults(populationResults) {
      if (populationResults.success) {
        this.successMessages.push('Memberships were successfully updated.')
        if (this.$_.size(populationResults.messages)) {
          this.successMessages = this.successMessages.concat(populationResults.messages)
        } else {
          this.successMessages.push('No changes in membership were found.')
        }
      } else {
        this.errorMessages.push('There were errors during the last membership update.')
        this.errorMessages = this.errorMessages.concat(populationResults.messages)
        this.errorMessages.push('You can attempt to correct the errors by running the update again.')
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
  .page-site-mailing-list-form {
    margin: 20px 0;
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
}
</style>
