<template>
  <div v-if="!contextStore.isLoading" class="pb-5 px-5">
    <div class="pl-3">
      <Header1 text="Manage Mailing Lists" />
      <div id="mailing-lists-alert" aria-live="polite">
        <v-alert
          v-if="error"
          class="my-3"
          density="compact"
          role="none"
          type="warning"
        >
          {{ error }}
        </v-alert>
      </div>
    </div>
    <div v-if="contextStore.currentUser.isAdmin || contextStore.currentUser.isCanvasAdmin" class="align-center d-flex flex-wrap px-3">
      <div class="pr-3">
        <v-text-field
          id="page-site-mailing-list-site-id"
          v-model="canvasSiteId"
          :aria-describedby="!!trim(canvasSiteId) && !isCanvasSiteIdValid ? 'mailing-list-site-id-messages' : null"
          aria-label="bCourses Course ID"
          aria-required="true"
          density="comfortable"
          :error="!!trim(canvasSiteId) && !isCanvasSiteIdValid"
          hide-details
          maxlength="10"
          label="bCourses Course ID"
          style="width: 200px"
          variant="outlined"
          @keydown.enter="proceed"
        />
        <span v-if="!!trim(canvasSiteId) && !isCanvasSiteIdValid" id="mailing-list-site-id-messages" class="position-absolute validation-messages">
          <span class="sr-only">Invalid entry. </span>{{ 'Only numbers allowed.' }}
        </span>
      </div>
      <div>
        <v-btn
          id="btn-get-mailing-list"
          color="primary"
          :disabled="isProcessing || !isCanvasSiteIdValid"
          size="large"
          @click="proceed"
        >
          <span v-if="!isProcessing">Get Mailing List</span>
          <span v-if="isProcessing">
            <SpinnerWithinButton /> Searching...
          </span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, nextTick, onMounted, ref} from 'vue'
import {trim} from 'lodash'
import {useRouter} from 'vue-router'
import Header1 from '@/components/utils/Header1.vue'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton'
import {alertScreenReader, isValidCanvasSiteId, putFocusNextTick} from '@/utils'
import {getMailingList} from '@/api/mailing-list'
import {useContextStore} from '@/stores/context'
import {useMailingListStore} from '@/stores/mailing-list'

const canvasSiteId = ref(undefined)
const contextStore = useContextStore()
const error = ref(undefined)
const isCanvasSiteIdValid = computed(() => {
  return isValidCanvasSiteId(canvasSiteId.value)
})
const isProcessing = ref(false)
const mailingListStore = useMailingListStore()
const router = useRouter()

contextStore.loadingStart()

onMounted(() => {
  if (contextStore.currentUser.isAdmin || contextStore.currentUser.isCanvasAdmin) {
    mailingListStore.init()
  } else {
    error.value = 'Unauthorized'
  }
  contextStore.loadingComplete()
})

const proceed = () => {
  if (!isProcessing.value) {
    isProcessing.value = true
    error.value = undefined
    alertScreenReader('Searching for mailing list.')
    const searchTimer = setInterval(() => {
      alertScreenReader('Still searching.')
    }, 7000)
    getMailingList(canvasSiteId.value).then(
      data => {
        if (data) {
          alertScreenReader('Mailing list found.', 'assertive')
          mailingListStore.setMailingList(data)
          router.push('/mailing_list/update')
        } else {
          alertScreenReader('No mailing list found.', 'assertive')
          nextTick(() => router.push(`/mailing_list/create/${canvasSiteId.value}`))
        }
      },
      error => {
        error.value = error
        isProcessing.value = false
        putFocusNextTick('btn-get-mailing-list')
      }
    ).finally(() => clearInterval(searchTimer))
  }
}
</script>
