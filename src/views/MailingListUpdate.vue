<template>
  <div v-if="!isLoading" class="canvas-application page-site-mailing-list">
    <h1 id="page-header" tabindex="-1">Update Mailing List</h1>
    <v-expansion-panels
      v-if="alerts.length"
      id="mailing-list-update-alert"
      v-model="openPanelIndex"
      color="info"
    >
      <v-expansion-panel
        v-for="(alert, index) in alerts"
        :key="index"
        :disabled="!$_.size(alert.emailAddresses)"
      >
        <v-expansion-panel-title :color="alert.type === 'errors' ? 'red' : 'success'">
          <span v-if="$_.size(alert.emailAddresses)">
            {{ alert.message }}
            [<span class="toggle-show-hide">{{ openPanelIndex === index ? 'hide' : 'show' }}</span><span class="sr-only"> users</span>]
          </span>
          <span v-if="!$_.size(alert.emailAddresses)" class="alert-message-without-email-addresses">
            {{ alert.message }}
          </span>
          <template #actions>
            <v-icon
              v-if="$_.size(alert.emailAddresses)"
              color="white"
              :icon="alert.type === 'errors' ? 'mdi-alert-circle' : 'mdi-check'"
            />
          </template>
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-list class="py-0" density="compact">
            <v-list-item
              v-for="emailAddress in alert.emailAddresses"
              :key="emailAddress"
              class="py-0"
              density="compact"
              rounded
            >
              <template #prepend>
                <v-icon
                  class="mr-4"
                  :color="alert.type === 'errors' ? 'red' : 'primary'"
                  icon="mdi-account"
                />
              </template>
              <v-list-item-subtitle>{{ emailAddress }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
    <div class="mt-4">
      <v-card id="mailing-list-details">
        <v-card-text>
          <h2>Canvas Course Site</h2>
          <v-container>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  Name:
                </div>
              </v-col>
              <v-col>
                <OutboundLink
                  id="mailing-list-course-site-name"
                  class="pr-2"
                  :href="canvasSite.url"
                >
                  {{ canvasSite.name }}
                </OutboundLink>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  ID:
                </div>
              </v-col>
              <v-col>
                {{ canvasSite.canvasSiteId }}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  Description:
                </div>
              </v-col>
              <v-col>
                {{ canvasSite.codeAndTerm }}
              </v-col>
            </v-row>
          </v-container>

          <h2>Mailing List</h2>
          <v-container>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  Name:
                </div>
              </v-col>
              <v-col>
                {{ mailingList.name }}@{{ mailingList.domain }}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  Count:
                </div>
              </v-col>
              <v-col>
                <div id="mailing-list-member-count">{{ pluralize('member', mailingList.membersCount, {0: 'No'}) }}</div>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  Last updated:
                </div>
              </v-col>
              <v-col>
                <div id="mailing-list-membership-last-updated">
                  <span v-if="mailingList.timeLastPopulated">
                    {{ $moment.unix(mailingList.timeLastPopulated.epoch).format('MMM D, YYYY') }}
                  </span>
                  <span v-if="!$_.get(mailingList, 'timeLastPopulated')">
                    Never.
                  </span>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
      <div class="d-flex justify-end mt-4">
        <v-btn
          id="btn-cancel"
          class="mr-2"
          variant="outlined"
          @click="cancel"
        >
          Cancel
        </v-btn>
        <v-btn
          id="btn-populate-mailing-list"
          class="mr-2"
          color="primary"
          @click="update"
        >
          <span v-if="!isUpdating">Update Memberships{{ hasUpdatedSincePageLoad ? ' Again' : '' }}</span>
          <span v-if="isUpdating">
            <SpinnerWithinButton /> Updating...
          </span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import MailingList from '@/mixins/MailingList.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {populateMailingList} from '@/api/mailing-list'
import {pluralize, putFocusNextTick} from '@/utils'

export default {
  name: 'MailingListUpdate',
  components: {OutboundLink, SpinnerWithinButton},
  mixins: [MailingList, Context],
  data: () => ({
    alerts: [],
    hasUpdatedSincePageLoad: false,
    isUpdating: false,
    messageType: undefined,
    openPanelIndex: [],
    showAlertDetails: false
  }),
  created() {
    if (this.mailingList && this.canvasSite) {
      if (this.updateSummary) {
        this.showUpdateSummary()
      }
      putFocusNextTick('page-header')
      this.$ready()
    } else {
      this.$router.push({path: '/mailing_list/select_course'})
    }
  },
  methods: {
    cancel() {
      this.$router.push({path: '/mailing_list/select_course'})
    },
    pluralize,
    showUpdateSummary() {
      const actions = ['add', 'remove', 'restore', 'update']
      const count = key => {
        let count = 0
        this.$_.each(actions, action => count += this.updateSummary[action][key].length)
        return count
      }
      const errorCount = count('errors')
      const successCount = count('successes')
      if (errorCount || successCount) {
        this.alerts = []
        this.$_.each(['errors', 'successes'], type => {
          this.$_.each(actions, action => {
            const summary = this.updateSummary[action]
            const emailAddresses = summary[type]
            if (emailAddresses.length) {
              const prefix = type === 'errors' ? `failed to ${action}` : (action === 'add' ? 'added ' : `${action}d `)
              const message = this.$_.capitalize(prefix + pluralize('user', emailAddresses.length) + '.')
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
    update() {
      this.$announcer.polite('Updating')
      this.alerts = []
      this.isUpdating = true
      populateMailingList(this.mailingList.id).then(
        data => {
          this.setMailingList(data.mailingList)
          this.setUpdateSummary(data.summary)
          this.showUpdateSummary()
        },
        error => {
          this.alerts = [{
            message: error,
            type: 'warning'
          }]
        }
      ).then(() => {
        this.isUpdating = false
        this.hasUpdatedSincePageLoad = true
      })
    }
  }
}
</script>

<style scoped lang="scss">
.alert-message-without-email-addresses {
  color: black !important;
  font-size: 16px;
  font-weight: 700;
}
.page-site-mailing-list {
  padding: 20px;

  .page-site-mailing-list-button-primary {
    margin: 0 4px;
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
</style>
