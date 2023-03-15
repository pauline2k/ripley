<template>
  <div v-if="!isLoading" class="canvas-application page-site-mailing-list">
    <h1 id="page-header" tabindex="-1">Update Mailing List</h1>
    <v-alert
      v-if="alert.message || $_.size(alert.items)"
      id="mailing-list-update-alert"
      class="mb-2"
      closable
      density="compact"
      role="alert"
      :type="alert.type"
    >
      <div v-if="alert.message">{{ alert.message }}</div>
      <ul v-if="$_.size(alert.items)">
        <li v-for="item in alert.items" :key="item">{{ item }}</li>
      </ul>
    </v-alert>
    <div class="mt-4">
      <v-card id="mailing-list-details">
        <v-card-text>
          <h2 id="mailing-list-details-header" tabindex="-1">Canvas Course Site</h2>
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
                {{ canvasSite.canvasCourseId }}
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

          <h2 id="mailing-list-details-header" tabindex="-1">Mailing List</h2>
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
          class="mr-1"
          variant="text"
          @click="cancel"
        >
          Exit
        </v-btn>
        <v-btn
          id="btn-populate-mailing-list"
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
import Utils from '@/mixins/Utils'
import {populateMailingList} from '@/api/mailing-list'

export default {
  name: 'MailingListUpdate',
  components: {OutboundLink, SpinnerWithinButton},
  mixins: [MailingList, Context, Utils],
  data: () => ({
    isUpdating: false,
    hasUpdatedSincePageLoad: false,
    alert: undefined,
    messageType: undefined
  }),
  created() {
    this.setAlert(undefined)
    if (this.mailingList && this.canvasSite) {
      this.$putFocusNextTick('page-header')
      this.$ready()
    } else {
      this.goToPath('/mailing_list/select_course')
    }
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
      this.$router.push({path: '/mailing_list/select_course'})
    },
    composeAlertMessage(errorCount, successCount) {
      let message
      if (errorCount > 1 && successCount > 1) {
        const describe = (count, noun, pluralize) => {
          return count ? `${count === 1 ? 'one' : count} ${noun}${count === 1 ? '' : pluralize}` : ''
        }
        const prefix = 'The update resulted in '
        message = prefix + describe(errorCount, 'error', 's')
        message += errorCount && successCount ? ' and ' : ''
        message += describe(successCount, 'success', 'es')
      }
      return message
    },
    setAlert(message, items, type) {
      this.alert = {message, items: items || [], type}
    },
    update() {
      this.setAlert(undefined)
      this.$announcer.polite('Updating')
      this.isUpdating = true
      this.alerts = {error: [], success: []}

      populateMailingList(this.canvasSite.canvasCourseId).then(
        data => {
          this.setMailingList(data.mailingList)
          const summary = data.summary
          const actions = ['add', 'remove', 'update']
          const count = key => {
            let count = 0
            this.$_.each(actions, action => count += summary[action][key].length)
            return count
          }
          const errorCount = count('errors')
          const successCount = count('successes')
          let message
          let items = []
          if (errorCount || successCount) {
            message = this.composeAlertMessage(errorCount, successCount)
            this.$_.each(['errors', 'successes'], key => {
              this.$_.each(actions, action => {
                const emailAddresses = summary[action][key]
                if (emailAddresses.length) {
                  const pastTense = action === 'add' ? 'added' : `${action}d`
                  const prefix = key === 'errors' ? `failed to ${action}` : `Successfully ${pastTense} `
                  items.push(prefix + this.oxfordJoin(emailAddresses))
                }
              })
            })
          } else {
            message = 'No changes made because no changes needed.'
          }
          this.setAlert(message, items, errorCount ? 'warning' : 'success')
        },
        error => {
          this.setAlert(error, 'warning', [])
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
</style>
