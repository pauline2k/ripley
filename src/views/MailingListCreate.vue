<template>
  <div v-if="!isLoading" class="canvas-application page-site-mailing-list">
    <h1 id="page-header" class="mt-0" tabindex="-1">Create Mailing List</h1>
    <Alert
      :closable="true"
      :error-message="error"
      :success-message="success"
    />
    <div class="mt-4">
      <v-card id="mailing-list-details" elevation="3">
        <v-card-title>
          <div class="pl-1 pt-2">
            <h2>Canvas Course Site</h2>
          </div>
        </v-card-title>
        <v-card-text>
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
        </v-card-text>
      </v-card>
      <div class="mx-5 mt-8">
        <h2>Create Mailing List</h2>
        <v-container fluid>
          <v-row no-gutters align="center">
            <v-col cols="1">
              <div class="float-right pr-3">
                <label for="mailing-list-name-input">Name:</label>
              </div>
            </v-col>
            <v-col cols="7">
              <v-text-field
                id="mailing-list-name-input"
                v-model="mailingListName"
                aria-required="true"
                hide-details
                maxlength="255"
                variant="outlined"
                required
                @keydown.enter="create"
              />
            </v-col>
            <v-col>
              <div class="d-flex">
                <div>
                  <v-btn
                    id="btn-cancel"
                    class="mr-1"
                    variant="text"
                    @click="cancel"
                  >
                    Cancel
                  </v-btn>
                </div>
                <div>
                  <v-btn
                    id="btn-create-mailing-list"
                    color="primary"
                    :disabled="isCreating || !$_.trim(mailingListName)"
                    @click="create"
                  >
                    <span v-if="!isCreating">Create mailing list</span>
                    <span v-if="isCreating">
                      <SpinnerWithinButton /> Creating...
                    </span>
                  </v-btn>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </div>
  </div>
</template>

<script>
import Alert from '@/components/utils/Alert'
import Context from '@/mixins/Context'
import MailingList from '@/mixins/MailingList.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {createMailingList, getSuggestedMailingListName} from '@/api/mailing-list'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'MailingListCreate',
  components: {Alert, OutboundLink, SpinnerWithinButton},
  mixins: [Context, MailingList],
  data: () => ({
    error: undefined,
    isCreating: false,
    mailingListName: undefined,
    success: undefined
  }),
  mounted() {
    if (this.canvasSite) {
      getSuggestedMailingListName(this.canvasSite.canvasSiteId).then(data => {
        this.mailingListName = data
        putFocusNextTick('page-header')
        this.$ready()
      })
    } else {
      this.$router.push({path: '/mailing_list/select_course'})
    }
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled.')
      this.$router.push({path: '/mailing_list/select_course'})
    },
    create() {
      this.error = this.success = null
      const name = this.$_.trim(this.mailingListName)
      if (name) {
        this.isCreating = true
        this.$announcer.polite('Creating list')
        createMailingList(this.canvasSite.canvasSiteId, name).then(
          data => {
            this.setMailingList(data)
            this.$router.push('/mailing_list/update')
          },
          error => this.error = error
        ).then(() => this.isCreating = false)
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
