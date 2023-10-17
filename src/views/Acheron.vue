<template>
  <div class="px-6 w-100">
    <Header1 text="Acheron (LV-426)" />
    <v-container class="ml-2 pt-0" fluid>
      <v-row>
        <v-col cols="12">
          <h2 class="mb-2">Canvas User Profile</h2>
        </v-col>
      </v-row>
      <v-row align="center" no-gutters>
        <v-col cols="8">
          <div class="align-center d-flex">
            <div class="mr-2">
              <v-text-field
                id="canvas-user-profile-by-uid"
                v-model="byUID"
                clearable
                density="compact"
                hide-details
                label="By UID"
                maxlength="10"
                style="width: 240px"
                variant="outlined"
                @focus="() => {
                  byCanvasUserId = null
                  canvasSiteId = null
                  canvasUserId = null
                }"
                @keydown.enter="fetchByUID"
              />
            </div>
            <v-btn
              id="canvas-user-profile-by-uid"
              :disabled="!trim(byUID) && !isValidUID(byUID)"
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
        </v-col>
      </v-row>
      <v-row align="center" class="pt-3" no-gutters>
        <v-col cols="8">
          <div class="align-center d-flex">
            <div class="mr-2">
              <v-text-field
                id="canvas-user-profile-by-uid"
                v-model="byCanvasUserId"
                clearable
                density="compact"
                hide-details
                label="By Canvas User ID"
                maxlength="10"
                style="width: 240px"
                variant="outlined"
                @focus="() => {
                  byUID = null
                  canvasSiteId = null
                  canvasUserId = null
                }"
                @keydown.enter="fetchByCanvasUserId"
              />
            </div>
            <v-btn
              id="canvas-user-profile-by-uid"
              :disabled="!trim(byCanvasUserId) || !isValidCanvasUserId(byCanvasUserId)"
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
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <h2 class="mb-2">Site User Profile</h2>
        </v-col>
      </v-row>
      <v-row align="center" no-gutters>
        <v-col cols="8">
          <div class="align-center d-flex">
            <div class="mr-2">
              <v-text-field
                id="canvas-site-id"
                v-model="canvasSiteId"
                clearable
                density="compact"
                hide-details
                label="Canvas Site ID"
                maxlength="10"
                style="width: 240px"
                variant="outlined"
                @focus="() => {
                  byCanvasUserId = null
                  byUID = null
                }"
                @keydown.enter="fetchCanvasSiteUserProfile"
              />
            </div>
            <div class="mr-2">
              <v-text-field
                id="canvas-user-profile-by-uid"
                v-model="canvasUserId"
                clearable
                density="compact"
                hide-details
                label="Canvas User ID"
                maxlength="10"
                style="width: 240px"
                variant="outlined"
                @focus="() => {
                  byCanvasUserId = null
                  byUID = null
                }"
                @keydown.enter="fetchCanvasSiteUserProfile"
              />
            </div>
            <v-btn
              id="canvas-user-profile-by-uid"
              :disabled="!trim(canvasSiteId) || !trim(canvasUserId) || !isValidCanvasSiteId(canvasSiteId) || !isValidCanvasUserId(canvasUserId)"
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
        </v-col>
      </v-row>
    </v-container>
    <v-divider class="mb-4 mt-8" />
    <h2>Payload</h2>
    <div
      v-if="error"
      aria-live="polite"
      class="font-italic font-weight-medium text-red"
      role="alert"
    >
      {{ error }}
    </div>
    <div class="payload-container">
      <pre>{{ payload }}</pre>
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
  margin-top: 10px;
  min-height: 100px;
  padding: 40px;
  width: 100%;
}
</style>
