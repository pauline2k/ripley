<template>
  <div v-if="!isLoading" class="canvas-application page-site-mailing-list">
    <h1>Mailing List</h1>

    <div v-if="alerts.error.length" role="alert" class="alert alert-error">
      <v-icon icon="mdi-exclamation-triangle" class="icon left icon-red canvas-notice-icon" />
      <div class="page-site-mailing-list-notice-message">
        <div v-for="error in alerts.error" :key="error">{{ error }}</div>
      </div>
    </div>

    <div v-if="errorMessages" role="alert" class="alert alert-error">
      <div v-for="errorMessage in errorMessages" :key="errorMessage">{{ errorMessage }}</div>
    </div>

    <div v-if="!errorMessages && mailingList.id" role="alert" class="alert alert-success">
      A Mailing List has been created at <strong>{{ mailingList.name }}@{{ mailingList.domain }}</strong>.
      Messages can now be sent through this address.
    </div>

    <div v-if="!errorMessages && !mailingList.id" class="alert">
      No Mailing List has yet been created for this site.
    </div>

    <p class="page-site-mailing-list-text">
      bCourses Mailing Lists allow Teachers, TAs, Lead TAs and Readers to send email to everyone in a bCourses site by
      giving the site its own email address. Messages sent to this address from the
      <strong>official berkeley.edu email address</strong>
      of a Teacher, TA, Lead TA or Reader will be sent to the official email addresses of all site
      members. Students and people not in the site cannot send messages through Mailing Lists.
    </p>

    <div v-if="!mailingList.id">
      <v-btn
        id="btn-create-mailing-list"
        class="canvas-button canvas-button-primary"
        color="primary"
        :disabled="errorMessages"
        @click="createMailingList"
      >
        <span v-if="!isCreating">Create mailing list</span>
        <span v-if="isCreating"><SpinnerWithinButton /> Creating...</span>
      </v-btn>
    </div>

    <div v-if="mailingList.id" class="border-top mt-3 pt-3">
      <h2 id="send-welcome-email-header" class="page-site-mailing-list-welcome-email-form-heading" tabindex="-1">
        Send Welcome Email
      </h2>
      <v-row no-gutters>
        <p class="page-site-mailing-list-text">
          The Welcome Email tool automatically sends a customizable message by email to all members of your course site, even if the site has not yet been published. For more information, visit <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0013900">https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0013900</OutboundLink>.
        </p>
      </v-row>

      <div v-if="emailFieldsPresent && !isWelcomeEmailActive" role="alert" class="alert alert-warning">
        Sending welcome emails is paused until activation.
      </div>

      <div v-if="alertEmailActivated" role="alert" class="alert alert-success">
        Welcome email activated.
      </div>

      <div v-if="emailFieldsPresent" class="page-site-mailing-list-welcome-email-toggle-outer">
        <label for="welcome-email-activation-toggle" class="page-site-mailing-list-welcome-email-toggle-label">
          Send email:
        </label>
        <div v-if="isWelcomeEmailActive" class="email-status email-status-active toggle-on">
          Active
        </div>
        <div v-if="!isWelcomeEmailActive" class="email-status email-status-paused">
          Paused
        </div>
        <div>
          <v-btn
            v-if="!isTogglingEmailActivation"
            id="welcome-email-activation-toggle"
            class="pl-1 pr-1"
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

      <div v-if="mailingList.welcomeEmailLastSent" class="page-site-mailing-list-text">
        <v-btn
          id="btn-download-sent-message-log"
          type="button"
          variant="text"
          class="p-0"
          @click="downloadMessageLog"
        >
          <v-icon icon="mdi-file-download" />
          Download sent message log (last updated {{ $moment(mailingList.welcomeEmailLastSent).format('MMM D, YYYY') }})
        </v-btn>
      </div>

      <form
        v-if="isEditingWelcomeEmail"
        class="canvas-page-form canvas-form page-site-mailing-list-welcome-email-form border-top"
        @submit.prevent="saveWelcomeEmail"
      >
        <v-row no-gutters>
          <label for="page-site-mailing-list-subject-input" class="page-site-mailing-list-welcome-email-form-heading">
            Subject
          </label>
        </v-row>
        <v-row no-gutters>
          <input id="page-site-mailing-list-subject-input" v-model="mailingListSubject" type="text">
        </v-row>
        <v-row no-gutters>
          <label for="page-site-mailing-list-message-input" class="page-site-mailing-list-welcome-email-form-heading">
            Message
          </label>
        </v-row>
        <v-row no-gutters>
          <div id="page-site-mailing-list-message-input" role="textbox" class="w-100 mb-4">
            <ckeditor
              v-model="mailingListMessage"
              class="w-100"
              :config="editorConfig"
              :editor="editor"
            ></ckeditor>
          </div>
        </v-row>
        <v-row no-gutters>
          <v-btn
            id="btn-save-welcome-email"
            color="primary"
            :disabled="!mailingListSubject || !mailingListMessage"
          >
            <span v-if="!isSavingWelcomeEmail">Save welcome email</span>
            <span v-if="isSavingWelcomeEmail">
              <SpinnerWithinButton /> Saving...
            </span>
          </v-btn>
          <v-btn
            v-if="emailFieldsPresent"
            id="btn-cancel-welcome-email-edit"
            color="secondary"
            @click="cancelEditMode"
          >
            Cancel
          </v-btn>
        </v-row>
      </form>

      <div v-if="!isEditingWelcomeEmail" class="border-top mt-3 pt-3">
        <div class="page-site-mailing-list-welcome-email-field-content">
          <h3 class="page-site-mailing-list-welcome-email-field-heading">
            Subject
          </h3>
          <div id="page-site-mailing-list-subject">
            {{ mailingList.welcomeEmailSubject }}
          </div>
        </div>
        <div class="page-site-mailing-list-welcome-email-field-content">
          <h3 class="page-site-mailing-list-welcome-email-field-heading">
            Message
          </h3>
          <div id="page-site-mailing-list-body" class="page-site-mailing-list-welcome-email-body" v-html="mailingList.welcomeEmailBody"></div>
        </div>
        <div class="page-site-mailing-list-welcome-email-field-content">
          <v-btn
            id="btn-edit-welcome-email"
            variant="text"
            class="p-0"
            @click="setEditMode"
          >
            Edit welcome email
          </v-btn>
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
  createSiteMailingList,
  deactivateWelcomeEmail,
  downloadWelcomeEmailCsv,
  getMailingList,
  updateWelcomeEmail
} from '@/api/mailing-list'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'SendWelcomeEmail',
  components: {
    SpinnerWithinButton,
    ckeditor: CKEditor.component,
    OutboundLink
  },
  mixins: [Context],
  data: () => ({
    alertEmailActivated: false,
    alerts: {
      error: [],
      success: []
    },
    editor: ClassicEditor,
    editorConfig: {
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link']
    },
    errorMessages: null,
    isCreating: false,
    isEditingWelcomeEmail: false,
    isSavingWelcomeEmail: false,
    isTogglingEmailActivation: false,
    isWelcomeEmailActive: false,
    mailingList: undefined,
    mailingListMessage: '',
    mailingListSubject: '',
  }),
  computed: {
    emailFieldsPresent() {
      return this.mailingList.welcomeEmailBody && this.mailingList.welcomeEmailSubject
    }
  },
  created() {
    getMailingList(this.currentUser.canvasSiteId).then(this.updateDisplay, this.$errorHandler)
  },
  methods: {
    cancelEditMode() {
      this.isEditingWelcomeEmail = false
      this.mailingListMessage = this.mailingList.welcomeEmailBody
      this.mailingListSubject = this.mailingList.welcomeEmailSubject
      putFocusNextTick('send-welcome-email-header')
    },
    createMailingList() {
      this.$announcer.polite('Creating list')
      this.isCreating = true
      createSiteMailingList(this.currentUser.canvasSiteId, this.mailingList).then(
        response => {
          this.updateDisplay(response)
          this.$ready()
        },
        this.$errorHandler
      )
    },
    downloadMessageLog() {
      this.$announcer.polite('Downloading message log')
      downloadWelcomeEmailCsv(this.currentUser.canvasSiteId)
    },
    saveWelcomeEmail() {
      this.$announcer.polite('Saving welcome email')
      this.savingWelcomeEmail = true
      updateWelcomeEmail(this.currentUser.canvasSiteId, this.mailingListSubject, this.mailingListMessage).then(
        response => {
          this.updateDisplay(response)
          putFocusNextTick('send-welcome-email-header')
        },
        this.$errorHandler
      )
    },
    setEditMode() {
      this.alertEmailActivated = false
      this.isEditingWelcomeEmail = true
      putFocusNextTick('page-site-mailing-list-subject-input')
    },
    toggleEmailActivation() {
      this.alertEmailActivated = false
      this.isTogglingEmailActivation = true
      const toggleEmailActivation = this.isWelcomeEmailActive ? deactivateWelcomeEmail : activateWelcomeEmail
      toggleEmailActivation(this.currentUser.canvasSiteId).then((data) => {
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
      this.mailingListMessage = this.mailingList.welcomeEmailBody
      this.mailingListSubject = this.mailingList.welcomeEmailSubject
      this.errorMessages = this.mailingList.errorMessages
      this.isEditingWelcomeEmail = this.mailingList.id && (!this.mailingListMessage && !this.mailingListSubject)
      this.isCreating = false
      this.isLoading = false
      this.$ready()
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
.page-site-mailing-list-welcome-email-body ol {
  margin: 0 0 10px 20px;
}
.page-site-mailing-list-welcome-email-body p {
  margin: 0 0 10px 0;
}
.page-site-mailing-list-welcome-email-body ul {
  list-style-type: disc;
  margin: 0 0 10px 20px;
}
</style>

<style scoped lang="scss">
.page-site-mailing-list {
  padding: 20px;

  .page-site-mailing-list-notice-message {
    margin-left: 30px;
  }

  .page-site-mailing-list-text {
    font-size: 14px;
    font-weight: 300;
    line-height: 1.6;
    margin: 15px;
  }

  .page-site-mailing-list-welcome-email-form {
    margin: 15px 15px 0 0;
    padding: 15px 0 0 15px;
  }

  .page-site-mailing-list-welcome-email-body ol {
    margin-left: 20px;
  }

  .page-site-mailing-list-welcome-email-body ul {
    margin-left: 20px;
  }

  .page-site-mailing-list-welcome-email-field-content {
    font-size: 14px;
    font-weight: 300;
    line-height: 1.6;
    margin: 0 0 15px 15px;
  }

  .page-site-mailing-list-welcome-email-field-heading {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.6;
    margin: 0 0 5px 0;
    padding: 0;
  }

  .page-site-mailing-list-welcome-email-form-heading {
    font-size: 18px;
    font-weight: 600;
  }

  .page-site-mailing-list-welcome-email-toggle-label {
    font-size: 14px;
    font-weight: 600;
    padding-right: 15px;
  }

  .page-site-mailing-list-welcome-email-toggle-outer {
    display: flex;
    margin: 15px;
  }

  .email-status {
    font-size: 12px;
    text-transform: uppercase;
  }

  .email-status-active {
    font-weight: 600;
  }

  .email-status-paused {
    color: #999999;
  }

  .toggle {
    font-size: 20px;
  }

  .toggle-off {
    color: #999999;
  }

  .toggle-on {
    color: #00c13a;
  }
}
</style>
