<template>
  <div v-if="!isLoading" class="pa-3">
    <div class="d-flex flex-column-reverse">
      <div id="mailing-lists-alert" aria-live="polite">
        <v-alert
          v-if="showCreatedAlert && !hasUpdatedSincePageLoad"
          id="mailing-list-created-alert"
          class="my-2"
          density="compact"
          role="alert"
          type="info"
        >
          The list "{{ mailingList.name }}@{{ mailingList.domain }}" has been created.
          To add members, click the "Update Memberships" button below.
        </v-alert>
      </div>
      <Header1 text="Update Mailing List" />
    </div>
    <div aria-live="polite">
      <v-expansion-panels
        v-if="alerts.length"
        id="mailing-list-update-alert"
        v-model="openPanelIndex"
        color="info"
      >
        <v-expansion-panel
          v-for="(alert, index) in alerts"
          :key="index"
          :disabled="!size(alert.emailAddresses)"
        >
          <v-expansion-panel-title
            :id="`mailing-list-alert-${index}`"
            :aria-controls="`mailing-list-alert-panel-${index}`"
            :color="alert.type === 'warning' ? 'error' : 'success'"
          >
            <span v-if="size(alert.emailAddresses)">
              {{ alert.message }}
              [&ThinSpace;<span class="toggle-show-hide">{{ openPanelIndex === index ? 'hide' : 'show' }}</span><span class="sr-only"> users</span>&ThinSpace;]
            </span>
            <span v-if="!size(alert.emailAddresses)" class="alert-message-without-email-addresses">
              {{ alert.message }}
            </span>
            <template #actions>
              <v-icon
                v-if="size(alert.emailAddresses)"
                color="white"
                :icon="alert.type === 'errors' ? mdiAlertCircle : mdiCheck"
              />
            </template>
          </v-expansion-panel-title>
          <v-expansion-panel-text :id="`mailing-list-alert-panel-${index}`">
            <ul id="mailing-list-members" class="pt-2">
              <li
                v-for="emailAddress in alert.emailAddresses"
                :key="emailAddress"
              >
                <v-icon
                  class="mr-6"
                  :color="alert.type === 'errors' ? 'red' : 'primary'"
                  :icon="mdiAccount"
                />
                {{ emailAddress }}
              </li>
            </ul>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </div>
    <div class="mt-2">
      <v-card id="mailing-list-details" class="pl-3">
        <v-card-text>
          <h2>Canvas Course Site</h2>
          <v-container class="py-3" fluid>
            <v-row no-gutters>
              <v-col cols="2">
                <label for="mailing-list-course-site-name" class="float-right font-weight-medium pr-3">
                  Name
                </label>
              </v-col>
              <v-col>
                <div>
                  <OutboundLink
                    id="mailing-list-course-site-name"
                    class="d-flex align-center"
                    :href="canvasSite.url"
                    title="View course site"
                  >
                    <span class="font-size-15 font-weight-medium pr-1">{{ canvasSite.name }}</span>
                    <v-icon :icon="mdiOpenInNew" size="small" />
                  </OutboundLink>
                </div>
              </v-col>
            </v-row>
            <v-row class="pt-1" no-gutters>
              <v-col cols="2">
                <label for="mailing-list-course-site-id" class="float-right font-weight-medium pr-3">
                  Canvas Site ID
                </label>
              </v-col>
              <v-col>
                <div id="mailing-list-course-site-id">
                  {{ canvasSite.canvasSiteId }}
                </div>
              </v-col>
            </v-row>
            <v-row class="pt-1" no-gutters>
              <v-col cols="2">
                <label for="mailing-list-course-site-code" class="float-right font-weight-medium pr-3">
                  Description
                </label>
              </v-col>
              <v-col>
                <div id="mailing-list-course-site-code">
                  {{ canvasSite.codeAndTerm }}
                </div>
              </v-col>
            </v-row>
          </v-container>

          <h2 class="mt-3">Mailing List</h2>
          <v-container class="py-3" fluid>
            <v-row no-gutters>
              <v-col cols="2">
                <label for="mailing-list-name" class="float-right font-weight-medium pr-3">
                  Name
                </label>
              </v-col>
              <v-col>
                <div id="mailing-list-name">
                  {{ mailingList.name }}@{{ mailingList.domain }}
                </div>
              </v-col>
            </v-row>
            <v-row class="pt-1" no-gutters>
              <v-col cols="2">
                <label for="mailing-list-member-count" class="float-right font-weight-medium pr-3">
                  Member count
                </label>
              </v-col>
              <v-col>
                <div id="mailing-list-member-count">{{ mailingList.membersCount }}</div>
              </v-col>
            </v-row>
            <v-row class="pt-1" no-gutters>
              <v-col cols="2">
                <label for="mailing-list-membership-last-updated" class="float-right font-weight-medium pr-3">
                  Last updated
                </label>
              </v-col>
              <v-col>
                <div id="mailing-list-membership-last-updated">
                  <span v-if="mailingList.populatedAt">
                    {{ $moment(mailingList.populatedAt).format('MMM D, YYYY') }}
                  </span>
                  <span v-if="!get(mailingList, 'populatedAt')">
                    Never
                  </span>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
      <div class="d-flex justify-end mt-4">
        <v-btn
          id="btn-populate-mailing-list"
          class="mr-2"
          color="primary"
          :disabled="isUpdating"
          @click="update"
        >
          <span v-if="!isUpdating">Update Memberships{{ hasUpdatedSincePageLoad ? ' Again' : '' }}</span>
          <span v-if="isUpdating">
            <SpinnerWithinButton /> Updating...
          </span>
        </v-btn>
        <v-btn
          id="btn-cancel"
          class="mr-2"
          :disabled="isUpdating"
          variant="tonal"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiAccount, mdiAlertCircle, mdiCheck, mdiOpenInNew} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import MailingList from '@/mixins/MailingList.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {capitalize, each, get, size} from 'lodash'
import {nextTick} from 'vue'
import {populateMailingList} from '@/api/mailing-list'
import {pluralize, putFocusNextTick} from '@/utils'

export default {
  name: 'MailingListUpdate',
  components: {Header1, OutboundLink, SpinnerWithinButton},
  mixins: [MailingList, Context],
  data: () => ({
    alerts: [],
    hasUpdatedSincePageLoad: false,
    isUpdating: false,
    messageType: undefined,
    openPanelIndex: [],
    showAlertDetails: false,
    showCreatedAlert: true
  }),
  created() {
    if (this.mailingList && this.canvasSite) {
      if (this.updateSummary) {
        this.showUpdateSummary()
      }
      this.$ready()
    } else {
      this.$router.push({path: '/mailing_list/select_course'})
    }
  },
  methods: {
    cancel() {
      this.alertScreenReader('Canceled. Nothing saved.', 'assertive')
      nextTick(this.$router.push({path: '/mailing_list/select_course'}))
    },
    get,
    pluralize,
    showUpdateSummary() {
      const actions = ['add', 'remove', 'restore', 'update']
      const count = key => {
        let count = 0
        each(actions, action => count += this.updateSummary[action][key].length)
        return count
      }
      const errorCount = count('errors')
      const successCount = count('successes')
      if (errorCount || successCount) {
        this.alerts = []
        each(['errors', 'successes'], type => {
          each(actions, action => {
            const summary = this.updateSummary[action]
            const emailAddresses = summary[type]
            if (emailAddresses.length) {
              const prefix = type === 'errors' ? `failed to ${action}` : (action === 'add' ? 'added ' : `${action}d `)
              const message = capitalize(prefix + pluralize('user', emailAddresses.length) + '.')
              this.alerts.push({action, emailAddresses, message, summary, type})
            }
          })
        })
      } else {
        this.alerts = [{
          message: 'Everything is up-to-date. No changes necessary.',
          type: 'info'
        }]
      }
    },
    size,
    update() {
      this.alerts = []
      this.alertScreenReader('Updating mailing list.')
      this.isUpdating = true
      this.showCreatedAlert = false
      let updateTimer = setInterval(() => {
        this.alertScreenReader('Still processing updates.')
      }, 7000)
      populateMailingList(this.mailingList.id).then(
        data => {
          this.alertScreenReader('Success.', 'assertive')
          this.setMailingList(data.mailingList)
          this.setUpdateSummary(data.summary)
          this.showUpdateSummary()
        },
        error => {
          this.alertScreenReader('Error.', 'assertive')
          this.alerts = [{
            message: error,
            type: 'warning'
          }]
        }
      ).then(() => this.hasUpdatedSincePageLoad = true
      ).finally(() => {
        clearInterval(updateTimer)
        this.isUpdating = false
        putFocusNextTick('btn-populate-mailing-list')
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.alert-message-without-email-addresses {
  font-size: 16px;
  font-weight: 700;
}
.toggle-show-hide {
  color: lightblue;
  text-decoration: none;
  &:hover {
    cursor: pointer;
  }
  &:hover, &:focus {
    text-decoration: underline;
  }
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
button:hover, :focus, :focus-visible {
  .toggle-show-hide {
    text-decoration: underline;
  }
}
li {
  height: 30px;
  padding-inline: 16px;
}
ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
</style>
