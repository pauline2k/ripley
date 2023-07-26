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
            <span v-if="isWelcomeEmailActive">Welcome email activated.</span>
            <span v-if="!isWelcomeEmailActive">Sending welcome emails is paused until activation.</span>
          </v-alert>
          <v-switch
            v-model="isWelcomeEmailActive"
            :label="isWelcomeEmailActive ? 'Active' : 'Inactive'"
            color="success"
            hide-details
          />
        </div>
        <!--
        TODO: Can we delete?
        <div v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject">
          <div>
            <v-btn
              id="welcome-email-activation-toggle"
              @click="toggle"
              @keyup.down="toggle"
            >
              <div v-if="isTogglingEmailActivation" class="pl-2">
                <SpinnerWithinButton />
              </div>
              <span v-if="!isTogglingEmailActivation" class="status-toggle-label">
                <v-icon v-if="isWelcomeEmailActive" icon="mdi-toggle-on" class="toggle toggle-on" />
                <v-icon v-if="!isWelcomeEmailActive" icon="mdi-toggle-off" class="toggle toggle-off" />
              </span>
            </v-btn>
          </div>
        </div>
        -->
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
        <div class="mt-1">
          <label for="input-subject" class="font-weight-medium text-subtitle-1">
            Subject
          </label>
          <div v-if="isEditingWelcomeEmail">
            <v-text-field
              id="input-subject"
              v-model="subject"
              density="compact"
              hide-details
              variant="outlined"
              @keydown.enter="saveWelcomeEmail"
            />
          </div>
          <div v-if="!isEditingWelcomeEmail" id="page-site-mailing-list-subject">
            {{ mailingList.welcomeEmailSubject }}
          </div>
          <div class="mt-3">
            <label for="input-message" class="font-weight-medium text-subtitle-1">
              Message
            </label>
            <div v-if="isEditingWelcomeEmail">
              <ckeditor
                id="input-message"
                v-model="body"
                :config="editorConfig"
                :editor="editor"
              />
            </div>
            <div v-if="!isEditingWelcomeEmail">
              <div id="page-site-mailing-list-body" v-html="mailingList.welcomeEmailBody"></div>
            </div>
          </div>
          <div class="mt-3">
            <div v-if="isEditingWelcomeEmail">
              <v-btn
                id="btn-save-welcome-email"
                class="mr-2"
                color="primary"
                :disabled="!isWelcomeEmailValid"
                @click="saveWelcomeEmail"
              >
                <span v-if="!isSavingWelcomeEmail">Save welcome email</span>
                <span v-if="isSavingWelcomeEmail">
                  <SpinnerWithinButton /> Saving...
                </span>
              </v-btn>
              <v-btn
                v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject"
                id="btn-cancel-welcome-email-edit"
                color="secondary"
                @click="cancelEditMode"
              >
                Cancel
              </v-btn>
            </div>
            <div v-if="!isEditingWelcomeEmail">
              <v-btn
                id="btn-edit-welcome-email"
                color="primary"
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
    editorConfig: {
      initialData: '',
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link']
    },
    errorMessages: [],
    isCreating: false,
    isEditingWelcomeEmail: false,
    isSavingWelcomeEmail: false,
    isTogglingEmailActivation: false,
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
      this.isEditingWelcomeEmail = false
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
        this.isSavingWelcomeEmail = true
        updateWelcomeEmail(false, this.body, this.subject).then(
          response => {
            this.updateDisplay(response)
            putFocusNextTick('send-welcome-email-header')
          },
          this.$errorHandler
        ).then(() => {
          this.isSavingWelcomeEmail = false
        })
      }
    },
    setEditMode() {
      this.isEditingWelcomeEmail = true
      putFocusNextTick('input-subject')
    },
    toggle() {
      this.isTogglingEmailActivation = true
      const toggleEmailActivation = this.isWelcomeEmailActive ? deactivateWelcomeEmail : activateWelcomeEmail
      toggleEmailActivation().then((data) => {
        this.isWelcomeEmailActive = !!data.welcomeEmailActive
        this.isTogglingEmailActivation = false
        this.$announcer.polite(`${this.isWelcomeEmailActive ? 'Enabled' : 'Disabled' } welcome email`)
      })
    },
    updateDisplay(data) {
      this.mailingList = data
      this.isWelcomeEmailActive = this.mailingList.welcomeEmailActive
      this.body = this.mailingList.welcomeEmailBody || ''
      this.subject = this.mailingList.welcomeEmailSubject
      this.errorMessages = this.mailingList.errorMessages || []
      this.isEditingWelcomeEmail = !this.body && !this.subject
      this.isCreating = false
    }
  }
}
</script>

<style>
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
