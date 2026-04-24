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
import Header1 from '@/components/utils/Header1.vue'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {isValidCanvasSiteId, isValidCanvasUserId, isValidUID} from '@/utils'
</script>

<script>
import {trim} from 'lodash'
import {getCanvasSiteUserProfile, getCanvasUserProfileById, getCanvasUserProfileByUID} from '@/api/canvas-user'

export default {
  name: 'Acheron',
  data: () => ({
    byCanvasUserId: undefined,
    canvasSiteId: undefined,
    canvasUserId: undefined,
    error: undefined,
    isFetchingByCanvasUserId: false,
    isFetchingByUID: false,
    isFetchingCanvasSiteUserProfile: false,
    payload: undefined,
    byUID: undefined
  }),
  computed: {
    disableAll() {
      return this.isFetchingByCanvasUserId || this.isFetchingByUID || this.isFetchingCanvasSiteUserProfile
    }
  },
  created() {
    this.$ready()
  },
  methods: {
    fetchByCanvasUserId() {
      this.isFetchingByCanvasUserId = true
      getCanvasUserProfileById(this.byCanvasUserId).then(this.setPayload, this.onError)
    },
    fetchByUID() {
      this.isFetchingByUID = true
      getCanvasUserProfileByUID(this.byUID).then(this.setPayload, this.onError)
    },
    fetchCanvasSiteUserProfile() {
      this.isFetchingCanvasSiteUserProfile = true
      getCanvasSiteUserProfile(this.canvasSiteId, this.canvasUserId).then(this.setPayload, this.onError)
    },
    onError(data) {
      this.resetFlags()
      this.payload = null
      this.error = data
    },
    resetFlags() {
      this.isFetchingByCanvasUserId = false
      this.isFetchingByUID = false
      this.isFetchingCanvasSiteUserProfile = false
    },
    setPayload(data) {
      this.resetFlags()
      this.error = null
      this.payload = data
    },
    trim
  }
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
