<template>
  <div v-if="!isLoading" class="page-user-provision">
    <Header1 id="page-title" class="page-user-provision-heading" text="Add Users to bCourses" />
    <form
      v-if="isAdmin"
      id="user-import-form"
      name="userImportForm"
      @submit.prevent="onSubmit"
    >
      <v-row no-gutters>
        <label for="page-user-provision-uid-list" class="user-provision-uid-label mb-2 mt-3">
          Type or paste a list of <span aria-hidden="true">UIDs</span><span class="sr-only">U I Deez</span> separated by spaces, commas, or line breaks
        </label>
        <textarea
          id="page-user-provision-uid-list"
          v-model="rawUids"
          :class="{'error': !isEmpty(validationErrors)}"
          rows="4"
          name="uids"
        />
      </v-row>
      <v-row no-gutters>
        <v-col aria-live="polite" cols="8" class="pt-2">
          <div
            v-if="!status"
            id="user-provision-validation-msg"
            class="validation-messages"
          >
            <div v-if="validationErrors.required">
              You must provide at least one
              <span aria-hidden="true">UID</span>
              <span class="sr-only">U I D</span>.
            </div>
            <div v-if="validationErrors.isNotNumeric">
              The following items in your list are not numeric: {{ invalidValues.join(', ') }}
            </div>
            <div v-if="validationErrors.isExceedingLimit">
              Maximum: 200 <span aria-hidden="true">UIDs</span><span class="sr-only">U I Deez</span>.
              {{ listLength }} <span aria-hidden="true">UIDs</span><span class="sr-only">U I Deez</span> found in list.
            </div>
          </div>
          <div
            v-if="status"
            id="user-provision-status-msg"
            class="mx-3"
          >
            <div v-if="status === 'error'">
              <v-icon class="text-red mr-2" :icon="mdiAlertCircleOutline" />
              <strong>Error: {{ error }}</strong>
            </div>
            <div v-if="status === 'success'" class="d-flex">
              <v-icon class="text-success mr-2" :icon="mdiCheckCircle" />
              <div>
                <div class="font-weight-bold">
                  Success: the following <template v-if="size(importedUids) > 1">
                    {{ size(importedUids) }} <span aria-hidden="true">UIDs</span><span class="sr-only">U I Deez</span> were
                  </template>
                  <template v-else>
                    UID was
                  </template> imported into bCourses.
                </div>
                <ul id="imported-uids-list" class="ml-3">
                  <li v-for="(uid, index) in importedUids" :key="index">{{ uid }}</li>
                </ul>
              </div>
            </div>
          </div>
        </v-col>
        <v-col cols="4">
          <div class="d-flex justify-end w-100">
            <v-btn
              id="user-provision-import-btn"
              aria-describedby="user-provisioning-progress"
              :aria-disabled="importButtonDisabled"
              class="text-no-wrap my-2"
              color="primary"
              :disabled="importButtonDisabled"
              type="submit"
            >
              <span v-if="!importProcessing">Import Users</span>
              <span v-if="importProcessing">
                <SpinnerWithinButton /> Importing Users...
              </span>
            </v-btn>
            <span id="user-provisioning-progress" class="sr-only" role="status">
              <span v-if="importProcessing">Importing Users</span>
            </span>
          </div>
        </v-col>
      </v-row>
    </form>
    <div aria-live="polite">
      <v-alert
        v-if="!isAdmin"
        class="font-weight-medium ma-2"
        density="compact"
        role="none"
        type="warning"
      >
        Unauthorized
      </v-alert>
    </div>
  </div>
</template>

<script setup>
import {each, isEmpty, size} from 'lodash'
import {mdiAlertCircleOutline, mdiCheckCircle} from '@mdi/js'
import {computed, onMounted, ref, watch} from 'vue'
import Header1 from '@/components/utils/Header1.vue'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {alertScreenReader} from '@/utils'
import {importUsers} from '@/api/canvas-utility'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const error = ref(undefined)
const importedUids = ref(undefined)
const importProcessing = ref(false)
const invalidValues = ref([])
const listLength = ref(undefined)
const rawUids = ref('')
const status = ref(undefined)
const validationErrors = ref({})
const importButtonDisabled = computed(() => {
  return importProcessing.value || isEmpty(rawUids.value)
})
const isAdmin = computed(() => {
  return contextStore.currentUser.isAdmin || contextStore.currentUser.isCanvasAdmin
})

watch(rawUids, () => {
  validationErrors.value = {}
})

onMounted(() => {
  contextStore.loadingComplete()
})

const handleError = errorMessage => {
  importProcessing.value = false
  status.value = 'error'
  error.value = errorMessage || 'Request to import users failed.'
}

const onSubmit = () => {
  const validatedUids = validateUids()
  let importTimer
  error.value = null
  importedUids.value = null
  status.value = null
  if (validatedUids) {
    importProcessing.value = true
    importTimer = setInterval(() => {
      alertScreenReader('Still processing user import')
    }, 7000)
    importUsers(validatedUids).then(response => {
      alertScreenReader('Imported users')
      importedUids.value = response.uids
      importProcessing.value = false
      rawUids.value = ''
      status.value = response.status
    }, handleError).catch(
      handleError
    ).finally(() => clearInterval(importTimer))
  }
}

const validateUids = () => {
  const uids = rawUids.value.match(/\w+/g)
  validationErrors.value = {}
  invalidValues.value = []
  if (!uids) {
    validationErrors.value.required = true
  }
  listLength.value = size(uids)
  if (listLength.value > 200) {
    validationErrors.value.isExceedingLimit = true
  }
  each(uids, uid => {
    if (isNaN(Number(uid))) {
      invalidValues.value.push(uid)
      validationErrors.value.isNotNumeric = true
    }
  })
  if (isEmpty(validationErrors.value)) {
    return uids.join()
  }
}
</script>

<style scoped lang="scss">
.page-user-provision {
  font-family: $body-font-family;
  font-size: 14px;
  padding: 10px 20px;
  .page-user-provision-heading {
    font-family: $body-font-family;
    font-size: 23px;
    font-weight: normal;
    margin: 10px 0;
  }
  .user-provision-uid-label {
    font-weight: 400;
  }
}
</style>
