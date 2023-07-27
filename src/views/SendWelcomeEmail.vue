<template>
  <div v-if="!isLoading" class="ma-5">
    <h1 id="page-header" tabindex="-1">Mailing List</h1>
    <v-alert
      density="compact"
      role="alert"
      type="success"
    >
      A Mailing List has been created at <strong>{{ mailingList.name }}@{{ mailingList.domain }}</strong>.
      Messages can now be sent through this address.
    </v-alert>
    <div>
      <div class="ml-3 mt-3">
        bCourses Mailing Lists allow Teachers, TAs, Lead TAs and Readers to send email to everyone in a bCourses site by
        giving the site its own email address. Messages sent to this address from the
        <strong>official berkeley.edu email address</strong>
        of a Teacher, TA, Lead TA or Reader will be sent to the official email addresses of all site
        members. Students and people not in the site cannot send messages through Mailing Lists.
      </div>
      <h2 id="send-welcome-email-header" class="my-3" tabindex="-1">
        Send Welcome Email
      </h2>
      <div class="mb-3 ml-3">
        The Welcome Email tool automatically sends a customizable message by email to all members of your course site,
        even if the site has not yet been published. For more information, visit
        <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0013900">
          https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0013900
        </OutboundLink>.
        <div v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject" class="mt-2">
          <v-alert
            density="compact"
            role="alert"
            :type="isWelcomeEmailActive ? 'success' : 'info'"
          >
            <span v-if="isWelcomeEmailActive">Welcome email {{ isToggling ? 'is being' : '' }} activated.</span>
            <span v-if="!isWelcomeEmailActive">Sending welcome emails is paused.</span>
          </v-alert>
          <div class="ml-5 w-25">
            <v-switch
              v-model="isWelcomeEmailActive"
              color="success"
              :disabled="isSaving || isToggling"
              hide-details
              @change="toggle"
            >
              <template #label>
                <v-progress-circular
                  v-if="isToggling"
                  indeterminate
                  size="24"
                  class="ms-2"
                />
                <span v-if="!isToggling">
                  {{ isWelcomeEmailActive ? 'Active' : 'Inactive' }}
                </span>
              </template>
            </v-switch>
          </div>
        </div>
        <div v-if="mailingList.welcomeEmailLastSent">
          <v-btn
            id="btn-download-sent-message-log"
            type="button"
            variant="text"
            @click="downloadMessageLog"
          >
            <v-icon icon="mdi-file-download" />
            Download sent message log (last updated {{ $moment(mailingList.welcomeEmailLastSent).format('MMM D, YYYY') }})
          </v-btn>
        </div>
        <div class="container pa-5">
          <label for="input-subject" class="font-weight-medium text-subtitle-1">
            Subject
          </label>
          <div v-if="isEditing">
            <v-text-field
              id="input-subject"
              v-model="subject"
              aria-required="true"
              class="bg-white"
              density="compact"
              hide-details
              maxlength="255"
              :rules="[s => !!s || 'Required']"
              variant="outlined"
              @keydown.enter="saveWelcomeEmail"
            />
          </div>
          <div v-if="!isEditing" id="page-site-mailing-list-subject">
            {{ mailingList.welcomeEmailSubject }}
          </div>
          <div class="mt-3">
            <label for="input-message" class="font-weight-medium text-subtitle-1">
              Message
            </label>
            <div v-if="isEditing">
              <ckeditor
                id="input-message"
                v-model="body"
                :config="{
                  codeBlock: {
                    indentSequence: '  '
                  },
                  initialData: '',
                  link: {
                    addTargetToExternalLinks: true,
                    defaultProtocol: 'http://'
                  },
                  toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link']
                }"
                :editor="editor"
                tag-name="textarea"
              />
            </div>
            <div v-if="!isEditing" class="pb-3 pt-1">
              <div id="page-site-mailing-list-body" v-html="mailingList.welcomeEmailBody"></div>
            </div>
          </div>
          <div class="mt-3">
            <div v-if="isEditing">
              <v-btn
                id="btn-save-welcome-email"
                class="mr-2"
                color="primary"
                :disabled="isSaving || isToggling || !isWelcomeEmailValid"
                @click="saveWelcomeEmail"
              >
                <span v-if="!isSaving">Save welcome email</span>
                <span v-if="isSaving">
                  <SpinnerWithinButton /> Saving...
                </span>
              </v-btn>
              <v-btn
                v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject"
                id="btn-cancel-welcome-email-edit"
                color="secondary"
                :disabled="isSaving || isToggling"
                @click="cancelEditMode"
              >
                Cancel
              </v-btn>
            </div>
            <div v-if="!isEditing">
              <v-btn
                id="btn-edit-welcome-email"
                color="primary"
                :disabled="isToggling"
                @click="setEditMode"
              >
                Edit welcome email
              </v-btn>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CKEditor from '@ckeditor/ckeditor5-vue'
import ClassicEditor from '@ckeditor/ckeditor5-build-classic'
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {
  activateWelcomeEmail,
  deactivateWelcomeEmail,
  downloadWelcomeEmailCsv,
  getMyMailingList,
  updateWelcomeEmail
} from '@/api/mailing-list'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'SendWelcomeEmail',
  components: {
    ckeditor: CKEditor.component,
    OutboundLink,
    SpinnerWithinButton
  },
  mixins: [Context],
  data: () => ({
    alerts: {
      error: [],
      success: []
    },
    body: '',
    editor: ClassicEditor,
    errorMessages: [],
    isCreating: false,
    isEditing: false,
    isSaving: false,
    isToggling: false,
    isWelcomeEmailActive: false,
    mailingList: undefined,
    subject: ''
  }),
  computed: {
    isWelcomeEmailValid() {
      return !!this.$_.trim(this.subject) && !!this.$_.trim(this.body)
    }
  },
  created() {
    getMyMailingList().then(
      data => {
        this.updateDisplay(data)
        this.$ready('Mailing List', 'page-header')
      },
      this.$errorHandler
    )
  },
  methods: {
    cancelEditMode() {
      this.isEditing = false
      this.body = this.mailingList.welcomeEmailBody || ''
      this.subject = this.mailingList.welcomeEmailSubject
      putFocusNextTick('send-welcome-email-header')
    },
    downloadMessageLog() {
      this.$announcer.polite('Downloading message log')
      downloadWelcomeEmailCsv()
    },
    saveWelcomeEmail() {
      if (this.isWelcomeEmailValid) {
        this.$announcer.polite('Saving welcome email')
        this.isSaving = true
        updateWelcomeEmail(false, this.body, this.subject).then(
          response => {
            this.updateDisplay(response)
            putFocusNextTick('send-welcome-email-header')
          },
          this.$errorHandler
        ).then(() => {
          this.isSaving = false
        })
      }
    },
    setEditMode() {
      this.isEditing = true
      putFocusNextTick('input-subject')
    },
    toggle() {
      this.isToggling = true
      const toggleEmailActivation = this.isWelcomeEmailActive ? activateWelcomeEmail : deactivateWelcomeEmail
      toggleEmailActivation().then(data => {
        this.isWelcomeEmailActive = !!data.welcomeEmailActive
        this.isToggling = false
        this.$announcer.polite(`${this.isWelcomeEmailActive ? 'Enabled' : 'Disabled' } welcome email`)
      })
    },
    updateDisplay(data) {
      this.mailingList = data
      this.isWelcomeEmailActive = this.mailingList.welcomeEmailActive
      this.body = this.mailingList.welcomeEmailBody || ''
      this.subject = this.mailingList.welcomeEmailSubject
      this.errorMessages = this.mailingList.errorMessages || []
      this.isEditing = !this.body && !this.subject
      this.isCreating = false
    }
  }
}
</script>

<style>
ol {
  margin-left: 16px;
}
ul {
  margin-left: 16px;
}
.ck.ck-editor__editable_inline {
  min-height: 150px;
  padding: 0 15px;
}
.ck.ck-editor__editable_inline ol {
  margin: 0 0 10px 20px;
}
.ck.ck-editor__editable_inline p {
  margin: 0 0 10px 0;
}
.ck.ck-editor__editable_inline ul {
  list-style-type: disc;
  margin: 0 0 10px 20px;
}
</style>
