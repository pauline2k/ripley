<template>
  <div v-if="!isLoading" class="canvas-application mx-10 my-5">
    <h1 id="page-header" class="my-3" tabindex="-1">Create Mailing List</h1>
    <v-alert
      v-if="!error && !isCreating && !success"
      density="compact"
      role="alert"
      type="info"
    >
      <span v-if="$isInIframe">No Mailing List has been created for bCourses site.</span>
      <span v-if="!$isInIframe">
        No Mailing List has been created for bCourses site
        <OutboundLink id="mailing-list-course-site-name" class="text-white" :href="canvasSite.url">
          <span class="font-weight-bold">{{ canvasSite.name }}</span>
        </OutboundLink>.
      </span>
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
      :closable="true"
      density="compact"
      role="alert"
      type="warning"
    >
      {{ error }}
    </v-alert>
    <div class="mt-2">
      <v-card id="mailing-list-details" elevation="1">
        <v-card-text>
          bCourses Mailing Lists allow Teachers, TAs, Lead TAs and Readers to send email to everyone in a bCourses site
          by giving the site its own email address. Messages sent to this address from the
          <span class="font-weight-bold">official berkeley.edu email address</span> of a Teacher, TA, Lead TA or Reader
          will be sent to the official email addresses of all site members. Students and people not in the site cannot
          send messages through Mailing Lists.
          <div class="mt-2">
            <v-container class="py-2 pl-0" fluid>
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
                          hide-details
                          maxlength="255"
                          required
                          variant="outlined"
                          @keydown.enter="create"
                        />
                        <div v-if="hasInvalidCharacters" class="has-invalid-characters">
                          <div class="d-flex text-red">
                            <div class="pr-1 text-no-wrap">Name may contain neither spaces nor: </div>
                            <div><pre>{{ $_.join([...$_.trim(invalidCharacters)], ' ') }}</pre></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </v-col>
                <v-col>
                  <div class="d-flex float-right">
                    <div v-if="currentUser.isAdmin">
                      <v-btn
                        id="btn-cancel"
                        class="mx-1"
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
import {createMailingList, getSuggestedMailingListName} from '@/api/mailing-list'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'MailingListCreate',
  components: {OutboundLink, SpinnerWithinButton},
  mixins: [Context, MailingList],
  data: () => ({
    error: undefined,
    invalidCharacters: ' "(),:;<>@[\\]',
    isCreating: false,
    mailingListName: undefined,
    success: undefined
  }),
  computed: {
    hasInvalidCharacters() {
      const name = this.$_.trim(this.mailingListName)
      return !!this.$_.intersection([...name], [...this.invalidCharacters]).length
    }
  },
  mounted() {
    if (this.currentUser.isTeaching || this.currentUser.isAdmin) {
      if (this.canvasSite) {
        getSuggestedMailingListName().then(data => {
          this.mailingListName = data
          putFocusNextTick('page-header')
          this.$ready()
        })
      } else {
        this.$router.push({path: '/mailing_list/select_course'})
      }
    } else {
      this.$router.push({path: '/404'})
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
      if (name && !this.hasInvalidCharacters) {
        this.isCreating = true
        this.$announcer.polite('Creating list')
        createMailingList(name).then(
          data => {
            this.setMailingList(data)
            this.$router.push('/mailing_list/send_welcome_email')
          },
          error => this.error = error
        ).then(() => this.isCreating = false)
      }
    }
  }
}
</script>

<style scoped lang="scss">
.has-invalid-characters {
  min-height: 24px;
}
.mailing-list-name-input {
  padding: 10px 8px 0 0;
}
</style>
