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
      <div class="mt-3 text-body-1">
        bCourses Mailing Lists allow Teachers, TAs, Lead TAs and Readers to send email to everyone in a bCourses site by
        giving the site its own email address. Messages sent to this address from the
        <strong>official berkeley.edu email address</strong>
        of a Teacher, TA, Lead TA or Reader will be sent to the official email addresses of all site
        members. Students and people not in the site cannot send messages through Mailing Lists.
      </div>
      <h2 id="send-welcome-email-header" class="mt-3" tabindex="-1">
        Send Welcome Email
      </h2>
      <div class="text-body-1">
        The Welcome Email tool automatically sends a customizable message by email to all members of your course site,
        even if the site has not yet been published. For more information, visit
        <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0013900">
          https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0013900
        </OutboundLink>.
      </div>
      <div>
        <v-switch
          v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject"
          v-model="isWelcomeEmailActive"
          label="Send email"
          color="success"
          hide-details
        />
        <v-alert
          v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject && !isWelcomeEmailActive"
          :closable="true"
          density="compact"
          role="alert"
          type="warning"
        >
          Sending welcome emails is paused until activation.
        </v-alert>
      </div>
      <v-alert
        v-if="alertEmailActivated"
        :closable="true"
        density="compact"
        role="alert"
        type="success"
      >
        Welcome email activated.
      </v-alert>
      <div v-if="mailingList.welcomeEmailBody && mailingList.welcomeEmailSubject">
        <div>
          <v-btn
            v-if="!isTogglingEmailActivation"
            id="welcome-email-activation-toggle"
            @click="toggleEmailActivation"
            @keyup.down="toggleEmailActivation"
          >
            <span class="status-toggle-label">
              <v-icon v-if="isWelcomeEmailActive" icon="mdi-toggle-on" class="toggle toggle-on" />
              <v-icon v-if="!isWelcomeEmailActive" icon="mdi-toggle-off" class="toggle toggle-off" />
            </span>
          </v-btn>
          <div v-if="isTogglingEmailActivation" class="pl-2">
            <SpinnerWithinButton />
          </div>
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
      <div v-if="isEditingWelcomeEmail" class="mt-3">
        <label for="input-subject" class="text-subtitle-1">
          Subject
        </label>
        <v-text-field
          id="input-subject"
          v-model="subject"
          density="compact"
          hide-details
          variant="outlined"
          @keydown.enter="saveWelcomeEmail"
        />
        <div class="mt-3">
          <label for="input-message" class="text-subtitle-1">
            Message
          </label>
          <ckeditor
            id="input-message"
            v-model="body"
            :config="editorConfig"
            :editor="editor"
          />
        </div>
        <div class="mt-3">
          <v-btn
            id="btn-save-welcome-email"
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
      </div>
      <div v-if="!isEditingWelcomeEmail" class="mt-3">
        <h3>
          Subject
        </h3>
        <div id="page-site-mailing-list-subject">
          {{ mailingList.welcomeEmailSubject }}
        </div>
        <h3>Message</h3>
        <div id="page-site-mailing-list-body" v-html="mailingList.welcomeEmailBody"></div>
        <v-btn
          id="btn-edit-welcome-email"
          variant="text"
          @click="setEditMode"
        >
          Edit welcome email
        </v-btn>
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
    alertEmailActivated: false,
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
      this.alertEmailActivated = false
      this.isEditingWelcomeEmail = true
      putFocusNextTick('input-subject')
    },
    toggleEmailActivation() {
      this.alertEmailActivated = false
      this.isTogglingEmailActivation = true
      const toggleEmailActivation = this.isWelcomeEmailActive ? deactivateWelcomeEmail : activateWelcomeEmail
      toggleEmailActivation().then((data) => {
        this.isWelcomeEmailActive = !!data.welcomeEmailActive
        this.isTogglingEmailActivation = false
        if (this.isWelcomeEmailActive) {
          this.alertEmailActivated = true
        }
        this.$announcer.polite(`${this.isWelcomeEmailActive ? 'Actived' : 'Paused' } welcome email`)
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
