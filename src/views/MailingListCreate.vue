<template>
  <div v-if="!isLoading" class="mx-10 my-5">
    <div class="d-flex flex-column-reverse">
      <div id="mailing-lists-alert" aria-live="polite">
        <v-alert
          v-if="!error && !success"
          class="my-2"
          density="compact"
          role="alert"
          text="No Mailing List has been created for this site."
          type="info"
        />
        <v-alert
          v-if="success"
          class="my-2"
          :closable="true"
          density="compact"
          role="alert"
          :text="success"
          type="success"
        />
        <v-alert
          v-if="error"
          class="my-2"
          density="compact"
          role="alert"
          :text="error"
          type="warning"
        />
      </div>
      <Header1 text="Create Mailing List" />
    </div>
    <div v-if="!error && !currentUser.isStudent" class="mt-2">
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
                    <OutboundLink
                      id="course-site-href"
                      class="d-flex align-center mb-2"
                      :href="canvasSite.url"
                      title="View course site"
                    >
                      <div class="font-size-20 pr-1" level="2" role="heading">{{ canvasSite.name }}</div>
                      <v-icon :icon="mdiOpenInNew" size="small" />
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
                    <div>Site ID {{ canvasSite.canvasSiteId }}</div>
                  </div>
                </v-col>
              </v-row>
              <v-row align="center" no-gutters>
                <v-col class="pb-0" cols="8">
                  <div class="d-flex pt-1 text-subtitle-1">
                    <div class="float-right mailing-list-name-input">
                      <label for="mailing-list-name-input">Name</label>
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
              <v-row v-if="currentUser.isTeaching || currentUser.isAdmin" no-gutters>
                <v-col>
                  <div class="d-flex float-right">
                    <div :class="{'mr-2': isAdminToolMode}">
                      <v-btn
                        id="btn-create-mailing-list"
                        color="primary"
                        :disabled="isCreating || !trim(mailingListName) || hasInvalidCharacters"
                        @click="create"
                      >
                        <span v-if="!isCreating">Create mailing list</span>
                        <span v-if="isCreating">
                          <SpinnerWithinButton /> Creating...
                        </span>
                      </v-btn>
                    </div>
                    <div v-if="isAdminToolMode">
                      <v-btn
                        id="btn-cancel"
                        :disabled="isCreating"
                        variant="tonal"
                        @click="cancel"
                      >
                        Cancel
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

<script setup>
import {mdiOpenInNew} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import MailingList from '@/mixins/MailingList.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {createMailingList, getMailingList, getSuggestedMailingListName} from '@/api/mailing-list'
import {get, trim} from 'lodash'
import {getCanvasSite} from '@/api/canvas-site'
import {nextTick} from 'vue'
import {toInt} from '@/utils'

export default {
  name: 'MailingListCreate',
  components: {Header1, OutboundLink, SpinnerWithinButton},
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
      const name = trim(this.mailingListName)
      const isValid = name.length && name.match(this.validNameRegex).length === name.length && name[0].match(/[a-z]/)
      return !isValid
    }
  },
  mounted() {
    this.init()
    const canvasSiteIdFromRoute = toInt(get(this.$route, 'params.canvasSiteId'))
    this.isAdminToolMode = !!canvasSiteIdFromRoute
    this.canvasSiteId = canvasSiteIdFromRoute || this.currentUser.canvasSiteId
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
              this.$ready()
            })
          })
        }
      },
      error => {
        this.error = error
        this.$ready()
      }
    )
  },
  methods: {
    cancel() {
      this.alertScreenReader('Canceled. Nothing saved.', 'assertive')
      nextTick(this.$router.push({path: '/mailing_list/select_course'}))
    },
    create() {
      const name = trim(this.mailingListName)
      if (name && !this.hasInvalidCharacters) {
        this.isCreating = true
        this.alertScreenReader('Creating mailing list.')
        let createTimer = setInterval(() => {
          this.alertScreenReader('Still creating mailing list.')
        }, 7000)
        createMailingList(this.canvasSiteId, name, !this.isAdminToolMode).then(
          data => {
            this.alertScreenReader('Success.', 'assertive')
            this.error = null
            this.setMailingList(data)
            nextTick(this.goToNextPage())
          },
          error => {
            this.alertScreenReader('Error.', 'assertive')
            this.error = error
          }
        ).finally(() => {
          clearInterval(createTimer)
          this.isCreating = false
        })
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
    },
    trim
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
