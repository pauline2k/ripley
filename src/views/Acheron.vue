<template>
  <div class="px-6 w-100">
    <Header1 text="Acheron (LV-426)" />
    <v-container class="pt-0" fluid>
      <v-row>
        <v-col cols="12" md="8">
          <h2 class="mb-2">Canvas User Profile</h2>
        </v-col>
      </v-row>
      <v-row align="center" no-gutters>
        <v-col cols="12" md="8">
          <div class="align-center d-flex flex-wrap flex-sm-nowrap">
            <v-text-field
              id="canvas-user-profile-by-uid"
              v-model="byUID"
              autocomplete="on"
              class="mr-3 my-1r"
              clearable
              density="compact"
              :disabled="disableAll"
              hide-details
              label="By UID"
              maxlength="10"
              max-width="15rem"
              min-width="10rem"
              variant="outlined"
              @focus="() => {
                byCanvasUserId = null
                canvasSiteId = null
                canvasUserId = null
              }"
              @keydown.enter="fetchByUID"
            />
            <div class="pr-3 w-100 w-sm-auto">
              <v-btn
                id="by-uid-btn"
                class="mr-3 my-1r w-100 w-sm-auto"
                :disabled="!trim(byUID) && !isValidUID(byUID) || disableAll"
                variant="tonal"
                @click="fetchByUID"
              >
                <span v-if="isFetchingByUID">
                  <SpinnerWithinButton /> Fetching...
                </span>
                <span v-if="!isFetchingByUID">
                  Fetch
                </span>
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row align="center" class="pt-4" no-gutters>
        <v-col cols="12" md="8">
          <div class="align-center d-flex flex-wrap flex-sm-nowrap">
            <v-text-field
              id="canvas-user-profile-by-id"
              v-model="byCanvasUserId"
              autocomplete="on"
              class="mr-3 my-1r"
              clearable
              density="compact"
              :disabled="disableAll"
              hide-details
              label="By Canvas User ID"
              maxlength="10"
              max-width="15rem"
              min-width="10rem"
              variant="outlined"
              @focus="() => {
                byUID = null
                canvasSiteId = null
                canvasUserId = null
              }"
              @keydown.enter="fetchByCanvasUserId"
            />
            <div class="pr-3 w-100 w-sm-auto">
              <v-btn
                id="by-ui-btn"
                class="mr-3 my-1r w-100 w-sm-auto"
                :disabled="!trim(byCanvasUserId) || !isValidCanvasUserId(byCanvasUserId) || disableAll"
                variant="tonal"
                @click="fetchByCanvasUserId"
              >
                <span v-if="isFetchingByCanvasUserId">
                  <SpinnerWithinButton /> Fetching...
                </span>
                <span v-if="!isFetchingByCanvasUserId">
                  Fetch
                </span>
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <h2 class="mb-2">Site User Profile</h2>
        </v-col>
      </v-row>
      <v-row align="center" no-gutters>
        <v-col cols="12" lg="8">
          <div class="align-center d-flex flex-wrap">
            <v-text-field
              id="canvas-site-id"
              v-model="canvasSiteId"
              autocomplete="on"
              class="mr-3 mt-1r"
              clearable
              density="compact"
              :disabled="disableAll"
              hide-details
              label="Canvas Site ID"
              maxlength="10"
              max-width="15rem"
              min-width="10rem"
              variant="outlined"
              @focus="() => {
                byCanvasUserId = null
                byUID = null
              }"
              @keydown.enter="fetchCanvasSiteUserProfile"
            />
            <v-text-field
              id="canvas-site-id-btn"
              v-model="canvasUserId"
              autocomplete="on"
              class="mr-3 mt-1r"
              clearable
              density="compact"
              :disabled="disableAll"
              hide-details
              label="Canvas User ID"
              maxlength="10"
              max-width="15rem"
              min-width="10rem"
              variant="outlined"
              @focus="() => {
                byCanvasUserId = null
                byUID = null
              }"
              @keydown.enter="fetchCanvasSiteUserProfile"
            />
            <div class="pr-3 w-100 w-sm-auto">
              <v-btn
                id="canvas-user-profile-by-uid"
                class="mr-3 mt-1r w-100 w-sm-auto"
                :disabled="!trim(canvasSiteId) || !trim(canvasUserId) || !isValidCanvasSiteId(canvasSiteId) || !isValidCanvasUserId(canvasUserId) || disableAll"
                variant="tonal"
                @click="fetchCanvasSiteUserProfile"
              >
                <span v-if="isFetchingCanvasSiteUserProfile">
                  <SpinnerWithinButton /> Fetching...
                </span>
                <span v-if="!isFetchingCanvasSiteUserProfile">
                  Fetch
                </span>
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
    <v-divider class="mb-4 mt-8" />
    <h2>Payload</h2>
    <div aria-live="polite">
      <v-alert
        v-if="error"
        id="error"
        class="mt-2"
        density="compact"
        role="none"
        :text="error"
        type="error"
      />
    </div>
    <div class="payload-container">
      <pre id="payload">{{ payload }}</pre>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {trim} from 'lodash'
import Header1 from '@/components/utils/Header1.vue'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {isValidCanvasSiteId, isValidCanvasUserId, isValidUID} from '@/utils'
import {getCanvasSiteUserProfile, getCanvasUserProfileById, getCanvasUserProfileByUID} from '@/api/canvas-user'
import {useContextStore} from '@/stores/context'

const byCanvasUserId = ref()
const canvasSiteId = ref()
const canvasUserId = ref()
const contextStore = useContextStore()
const error = ref()
const isFetchingByCanvasUserId = ref(false)
const isFetchingByUID = ref(false)
const isFetchingCanvasSiteUserProfile = ref(false)
const payload = ref()
const byUID = ref()

const disableAll = computed(() => {
  return isFetchingByCanvasUserId.value || isFetchingByUID.value || isFetchingCanvasSiteUserProfile.value
})

onMounted(() => {
  contextStore.loadingComplete()
})

const fetchByCanvasUserId = () => {
  isFetchingByCanvasUserId.value = true
  getCanvasUserProfileById(byCanvasUserId.value).then(setPayload, onError)
}

const fetchByUID = () => {
  isFetchingByUID.value = true
  getCanvasUserProfileByUID(byUID.value).then(setPayload, onError)
}

const fetchCanvasSiteUserProfile = () => {
  isFetchingCanvasSiteUserProfile.value = true
  getCanvasSiteUserProfile(canvasSiteId.value, canvasUserId.value).then(setPayload, onError)
}

const onError = data => {
  resetFlags()
  payload.value = null
  error.value = data
}

const resetFlags = () => {
  isFetchingByCanvasUserId.value = false
  isFetchingByUID.value = false
  isFetchingCanvasSiteUserProfile.value = false
}

const setPayload = data => {
  resetFlags()
  error.value = null
  payload.value = data
}
</script>

<style scoped lang="scss">
.payload-container {
  background-color: lightcyan;
  border: 1px solid #3a87ad;
  margin: 10px 0;
  min-height: 6.25rem;
  padding: 40px;
  width: 100%;
}
</style>
