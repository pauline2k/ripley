<template>
  <div v-if="!isLoading" class="canvas-application mx-10 my-5">
    <h1 id="page-header" class="my-3" tabindex="-1">Create Mailing List</h1>
    <v-alert
      v-if="!error && !isCreating && !success"
      density="compact"
      role="alert"
      type="info"
    >
      No Mailing List has been created for this site.
    </v-alert>
    <v-alert
      v-if="success"
      class="ma-2"
      :closable="true"
      density="compact"
      role="alert"
      type="success"
    >
      {{ success }}
    </v-alert>
    <v-alert
      v-if="error"
      class="ma-2"
      density="compact"
      role="alert"
      type="warning"
    >
      {{ error }}
    </v-alert>
    <div class="mt-2">
      <v-card id="mailing-list-details" elevation="1">
        <v-card-text>
          <div v-if="!isAdminToolMode" class="mb-1">
            bCourses Mailing Lists allow Teachers, TAs, Lead TAs and Readers to send email to everyone in a bCourses site
            by giving the site its own email address. Messages sent to this address from the
            <span class="font-weight-bold">official berkeley.edu email address</span> of a Teacher, TA, Lead TA or Reader
            will be sent to the official email addresses of all site members. Students and people not in the site cannot
            send messages through Mailing Lists.
          </div>
          <div>
            <v-container class="mb-2 pb-1 pl-0 pt-2" fluid>
              <v-row v-if="isAdminToolMode" no-gutters>
                <v-col cols="auto" class="me-auto">
                  <div v-if="canvasSite.url">
                    <OutboundLink id="course-site-href" :href="canvasSite.url">
                      <div class="d-flex">
                        <div class="pr-2">
                          <span class="sr-only">View course site </span>
                          <h2>{{ canvasSite.name }}</h2>
                        </div>
                        <div class="pb-1">
                          <v-icon icon="mdi-open-in-new" size="small" />
                        </div>
                      </div>
                    </OutboundLink>
                  </div>
                  <div v-if="!canvasSite.url">
                    <h2>{{ canvasSite.name }}</h2>
                  </div>
                </v-col>
              </v-row>
              <v-row v-if="isAdminToolMode" no-gutters>
                <v-col>
                  <div class="mb-4 w-auto">
                    <div v-if="canvasSite.term" class="text-subtitle-1">{{ canvasSite.term.name }}</div>
                    <div>Site ID: {{ canvasSite.canvasSiteId }}</div>
                  </div>
                </v-col>
              </v-row>
              <v-row no-gutters align="center">
                <v-col cols="8">
                  <div v-if="currentUser.isAdmin" class="d-flex pt-1 text-subtitle-1">
                    <div class="float-right mailing-list-name-input">
                      <label for="mailing-list-name-input">Name:</label>
                    </div>
                    <div class="w-100">
                      <div>
                        <v-text-field
                          id="mailing-list-name-input"
                          v-model="mailingListName"
                          aria-required="true"
                          density="comfortable"
                          :disabled="isCreating"
                          hide-details
                          maxlength="50"
                          required
                          variant="outlined"
                          @keydown.enter="create"
                        />
                        <div class="has-invalid-characters">
                          <div v-if="hasInvalidCharacters" class="d-flex text-red">
                            <div class="pr-1 text-no-wrap">
                              Only lowercase alphanumeric, underscore and hyphen characters allowed.
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </v-col>
              </v-row>
              <v-row v-if="currentUser.isTeaching || currentUser.isAdmin">
                <v-col>
                  <div class="d-flex float-right mt-1">
                    <div v-if="isAdminToolMode">
                      <v-btn
                        id="btn-cancel"
                        class="mx-1"
                        :disabled="isCreating"
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
                        :disabled="isCreating || !$_.trim(mailingListName) || hasInvalidCharacters"
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
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import MailingList from '@/mixins/MailingList.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {createMailingList, getMailingList, getSuggestedMailingListName} from '@/api/mailing-list'
import {getCanvasSite} from '@/api/canvas-site'
import {putFocusNextTick, toInt} from '@/utils'

export default {
  name: 'MailingListCreate',
  components: {OutboundLink, SpinnerWithinButton},
  mixins: [Context, MailingList],
  data: () => ({
    canvasSiteId: undefined,
    error: undefined,
    isAdminToolMode: undefined,
    isCreating: false,
    mailingListName: undefined,
    success: undefined,
    validNameRegex: /[a-z0-9_-]/g
  }),
  computed: {
    hasInvalidCharacters() {
      const name = this.$_.trim(this.mailingListName)
      const isValid = name.length && name.match(this.validNameRegex).length === name.length && name[0].match(/[a-z]/)
      return !isValid
    }
  },
  mounted() {
    this.init()
    this.canvasSiteId = toInt(this.$_.get(this.$route, 'params.canvasSiteId'))
    this.isAdminToolMode = !!this.canvasSiteId
    this.canvasSiteId = this.canvasSiteId || this.currentUser.canvasSiteId
    getMailingList(this.canvasSiteId).then(
      data => {
        this.setMailingList(data)
        if (data) {
          this.goToNextPage()
        } else {
          this.getCanvasSite().then(data => {
            this.setCanvasSite(data)
            getSuggestedMailingListName(this.canvasSiteId).then(data => {
              this.mailingListName = data
              putFocusNextTick('page-header')
              this.$ready()
            })
          })
        }
      },
      error => {
        this.error = error
        putFocusNextTick('page-header')
        this.$ready()
      }
    )
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled.')
      this.$router.push({path: '/mailing_list/select_course'})
    },
    create() {
      this.error = null
      const name = this.$_.trim(this.mailingListName)
      if (name && !this.hasInvalidCharacters) {
        this.isCreating = true
        this.$announcer.polite('Creating list')
        createMailingList(this.canvasSiteId, name, !this.isAdminToolMode).then(
          data => {
            this.setMailingList(data)
            this.goToNextPage()
          },
          error => this.error = error
        ).then(() => this.isCreating = false)
      }
    },
    getCanvasSite() {
      return new Promise(resolve => {
        if (this.canvasSite) {
          resolve(this.canvasSite)
        } else {
          getCanvasSite(this.canvasSiteId).then(resolve)
        }
      })
    },
    goToNextPage() {
      const path = this.isAdminToolMode ? '/mailing_list/update' : '/mailing_list/send_welcome_email'
      this.$router.push({path})
    }
  }
}
</script>

<style scoped lang="scss">
.has-invalid-characters {
  min-height: 28px;
}
.mailing-list-name-input {
  padding: 10px 8px 0 0;
}
</style>
