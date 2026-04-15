<template>
  <div v-if="!contextStore.isLoading" class="ma-5">
    <Header1 text="Mailing List" />
    <v-alert
      id="mailing-list-created-alert"
      density="compact"
      role="none"
      type="success"
    >
      A Mailing List has been created at <strong>{{ mailingList.name }}@{{ mailingList.domain }}</strong>.
      Messages can now be sent through this address.
    </v-alert>
    <div>
      <div class="ml-3 my-3">
        bCourses Mailing Lists allow Teachers, TAs, Lead TAs and Readers to send email to everyone in a bCourses site by
        giving the site its own email address. Messages sent to this address from the
        <strong>official berkeley.edu email address</strong>
        of a Teacher, TA, Lead TA or Reader will be sent to the official email addresses of all site
        members. Students and people not in the site cannot send messages through Mailing Lists.
      </div>
      <div v-if="get(mailingList, 'welcomeEmailLastSent')" class="mb-3">
        <h2 id="download-log-file-header" class="my-2" tabindex="-1">
          Download Log of Sent Messages
        </h2>
        <div class="ml-3">
          <div class="mb-2 my-1">
            <v-btn
              id="btn-download-sent-message-log"
              color="primary"
              :disabled="isDownloading || refreshing"
              @click="downloadMessageLog"
            >
              <span class="mr-1">
                <v-progress-circular
                  v-if="isDownloading"
                  class="mr-1"
                  indeterminate
                  size="18"
                  width="3"
                />
                <v-icon v-if="!isDownloading" :icon="mdiFileDownloadOutline" size="large" />
              </span>
              {{ isDownloading ? 'Downloading' : 'Download' }}
            </v-btn>
          </div>
          <div>
            <span class="font-weight-bold">NOTE:</span>
            Welcome email last sent on {{ $moment(mailingList.welcomeEmailLastSent).format('MMM D, YYYY') }}
          </div>
        </div>
      </div>
      <h2 id="send-welcome-email-header" class="ml-3 my-2" tabindex="-1">
        Send Welcome Email
      </h2>
      <div class="pb-3 pl-3">
        <div class="mb-3">
          The Welcome Email tool automatically sends a customizable message by email to all members of your course site,
          even if the site has not yet been published. For more information, visit
          <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0013900">
            How to Create a Welcome Email with the bCourses Mailing List
          </OutboundLink>.
        </div>
        <div class="mt-2">
          <v-alert
            v-if="!isWelcomeEmailValid"
            id="toggle-welcome-email-desc"
            density="compact"
            role="none"
            :type="isWelcomeEmailActive ? 'success' : 'info'"
          >
            You can activate the welcome email
            <span class="font-italic">after</span> you save a subject and message body below.
          </v-alert>
          <div class="ml-5 w-25">
            <v-switch
              id="toggle-welcome-email-active"
              v-model="isWelcomeEmailActive"
              :aria-describedby="isWelcomeEmailValid ? undefined : 'toggle-welcome-email-desc'"
              color="success"
              :disabled="!isWelcomeEmailValid || isSaving || isToggling"
              hide-details
              @change="toggle"
            >
              <template #label>
                <v-progress-circular
                  v-if="isToggling"
                  indeterminate
                  size="24"
                  class="mx-2"
                />
                <span class="text-no-wrap">
                  Activate welcome email
                </span>
              </template>
            </v-switch>
          </div>
        </div>
        <div class="container pb-5 pt-3 px-5">
          <template v-if="isEditing">
            <label id="input-subject-label" for="input-subject" class="text-subtitle-1">
              Subject
            </label>
            <v-text-field
              id="input-subject"
              v-model="subject"
              aria-required="true"
              autocomplete="on"
              class="bg-white"
              density="compact"
              hide-details
              maxlength="255"
              :rules="[s => !!s || 'Subject is required']"
              variant="outlined"
              @keydown.enter="saveWelcomeEmail"
            />
          </template>
          <template v-else>
            <div class="text-subtitle-1">
              Subject
            </div>
            <div id="page-site-mailing-list-subject">
              {{ get(mailingList, 'welcomeEmailSubject') }}
            </div>
          </template>
          <div class="mt-3">
            <template v-if="isEditing">
              <label id="input-message-label" for="input-message" class="text-subtitle-1">
                Message body
              </label>
              <v-textarea
                id="input-message"
                v-model="body"
                variant="outlined"
                bg-color="white"
                :rules="[s => !!s || 'Message body is required']"
              />
            </template>
            <template v-else>
              <div class="text-subtitle-1">
                Message body
              </div>
              <div class="pb-3 pt-1">
                <div
                  id="page-site-mailing-list-body"
                  v-html="get(mailingList, 'welcomeEmailBody')"
                />
              </div>
            </template>
          </div>
          <div class="mt-3">
            <div v-if="isEditing">
              <v-btn
                id="btn-save-welcome-email"
                class="mr-2"
                color="primary"
                :disabled="isSaving || isToggling || !isInputValid"
                @click="saveWelcomeEmail"
              >
                <span v-if="!isSaving">Save welcome email</span>
                <span v-if="isSaving">
                  <SpinnerWithinButton /> Saving...
                </span>
              </v-btn>
              <v-btn
                v-if="isWelcomeEmailValid"
                id="btn-cancel-welcome-email-edit"
                :disabled="isSaving || isToggling"
                variant="tonal"
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

<script setup>
import {computed, onMounted, ref} from 'vue'
import {get, trim} from 'lodash'
import {mdiFileDownloadOutline} from '@mdi/js'
import {storeToRefs} from 'pinia'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {
  activateWelcomeEmail,
  deactivateWelcomeEmail,
  downloadWelcomeEmailCsv,
  getMyMailingList,
  updateWelcomeEmail
} from '@/api/mailing-list'
import {alertScreenReader, putFocusNextTick} from '@/utils'
import {useContextStore} from '@/stores/context'
import {useMailingListStore} from '@/stores/mailing-list'

const body = ref('')
const contextStore = useContextStore()
const errorMessages = ref([])
const isCreating = ref(false)
const isDownloading = ref(false)
const isEditing = ref(false)
const isSaving = ref(false)
const isToggling = ref(false)
const isWelcomeEmailActive = ref(false)
const mailingListStore = useMailingListStore()
const {mailingList} = storeToRefs(mailingListStore)
const subject = ref('')
const isInputValid = computed(() => {
  return !!trim(subject.value) && !!trim(body.value)
})
const isWelcomeEmailValid = computed(() => {
  return !!(get(mailingList.value, 'welcomeEmailBody') && get(mailingList.value, 'welcomeEmailSubject'))
})

contextStore.loadingStart()

onMounted(() => {
  getMyMailingList().then(
    data => {
      updateDisplay(data)
      contextStore.loadingComplete()
    }
  )
})

const cancelEditMode = () => {
  isEditing.value = false
  body.value = get(mailingList.value, 'welcomeEmailBody') || ''
  subject.value = get(mailingList.value, 'welcomeEmailSubject')
  alertScreenReader('canceled')
  putFocusNextTick('btn-edit-welcome-email')
}

const downloadMessageLog = () => {
  isDownloading.value = true
  alertScreenReader('Downloading')
  downloadWelcomeEmailCsv().then(() => {
    isDownloading.value = false
    alertScreenReader('Downloaded.')
  })
}

const saveWelcomeEmail = () => {
  if (isInputValid.value) {
    alertScreenReader('Saving welcome email')
    isSaving.value = true
    updateWelcomeEmail(isWelcomeEmailActive.value, body.value, subject.value).then(
      response => {
        updateDisplay(response)
        alertScreenReader('Welcome email updated')
        putFocusNextTick('btn-edit-welcome-email')
      }
    ).then(() => {
      isSaving.value = false
    })
  }
}

const setEditMode = () => {
  isEditing.value = true
  putFocusNextTick('input-subject')
}

const toggle = () => {
  isToggling.value = true
  const toggleEmailActivation = isWelcomeEmailActive.value ? activateWelcomeEmail : deactivateWelcomeEmail
  toggleEmailActivation().then(data => {
    isWelcomeEmailActive.value = !!data.welcomeEmailActive
    isToggling.value = false
    putFocusNextTick('toggle-welcome-email-active')
  })
}
const updateDisplay = data => {
  mailingListStore.setMailingList(data)
  isWelcomeEmailActive.value = get(mailingList.value, 'welcomeEmailActive')
  body.value = get(mailingList.value, 'welcomeEmailBody') || ''
  subject.value = get(mailingList.value, 'welcomeEmailSubject')
  errorMessages.value = get(mailingList.value, 'errorMessages') || []
  isEditing.value = !body.value && !subject.value
  isCreating.value = false
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type -->
<style>
ol {
  margin-left: 16px;
}
ul {
  margin-left: 16px;
}
.v-selection-control--disabled {
  opacity: 0.6;
}
</style>
