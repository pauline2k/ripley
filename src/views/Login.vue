<template>
  <v-container
    class="background-splash"
    fill-height
    fluid
    :style="{backgroundImage: `url(${nostromoCrew})`}"
  >
    <Header1 id="page-title" class="sr-only" text="Login" />
    <v-row>
      <v-col v-if="!currentUser.isAuthenticated">
        <div class="py-5">
          <v-btn
            id="cas-auth-submit-button"
            @click="toCasLogin"
          >
            CalNet Login
          </v-btn>
        </div>
        <div>
          <hr />
        </div>
        <div v-if="config.devAuthEnabled" class="pt-3">
          <h2 class="sr-only">DevAuth</h2>
          <div class="w-50">
            <v-expand-transition>
              <v-alert
                v-if="devAuthError"
                border
                class="dev-auth-error mb-4 py-3"
                color="error"
                rounded
              >
                {{ devAuthError }}
              </v-alert>
            </v-expand-transition>
            <div class="pb-2">
              <v-text-field
                id="basic-auth-uid"
                v-model="uid"
                class="text-field"
                :disabled="isLoggingIn"
                hide-details
                label="UID"
                required
                variant="outlined"
                @keydown.enter="devAuth"
                @update:model-value="clearErrors"
              />
            </div>
            <div class="pb-2">
              <v-text-field
                id="basic-auth-password"
                v-model="password"
                autocomplete="off"
                class="my-2 text-field"
                :disabled="isLoggingIn"
                hide-details
                label="Password"
                required
                type="password"
                variant="outlined"
                @keydown.enter="devAuth"
                @update:model-value="clearErrors"
              />
            </div>
            <div class="pb-4">
              <v-text-field
                id="basic-auth-canvas-course-id"
                v-model="canvasSiteId"
                class="text-field"
                :disabled="isLoggingIn"
                hide-details
                label="Canvas Course ID (optional)"
                required
                variant="outlined"
                @keydown.enter="devAuth"
                @update:model-value="clearErrors"
              />
            </div>
            <v-btn
              id="basic-auth-submit-button"
              :disabled="disableSubmit || isLoggingIn"
              @click="devAuth"
            >
              <span v-if="isLoggingIn">
                <v-progress-circular
                  class="mr-1"
                  indeterminate
                  size="18"
                />
                Dev Auth
              </span>
              <span v-if="!isLoggingIn">Dev Auth</span>
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import Header1 from '@/components/utils/Header1.vue'
import nostromoCrew from '@/assets/images/nostromo-crew-eating-breakfast.png'
</script>

<script>
import Context from '@/mixins/Context'
import {get, trim} from 'lodash'
import {useContextStore} from '@/stores/context'
import {putFocusNextTick} from '@/utils'
import {devAuthLogIn, getCasLoginURL} from '@/api/auth'

export default {
  name: 'Login',
  mixins: [Context],
  data: () => ({
    canvasSiteId: undefined,
    devAuthError: undefined,
    isLoggingIn: false,
    password: undefined,
    showError: false,
    uid: undefined
  }),
  computed: {
    disableSubmit() {
      return !trim(this.password) || !trim(this.uid)
    }
  },
  created() {
    const showDevAuth = false
    this.$ready()
    return {showDevAuth}
  },
  methods: {
    clearErrors() {
      this.devAuthError = null
    },
    devAuth() {
      this.clearErrors()
      const canvasSiteId = trim(this.canvasSiteId)
      const password = trim(this.password)
      const uid = trim(this.uid)
      if (uid && password) {
        this.isLoggingIn = true
        devAuthLogIn(canvasSiteId, uid, password).then(
          data => {
            if (data.isAuthenticated) {
              useContextStore().setCurrentUser(data)
              this.alertScreenReader('You are logged in.')
              this.$router.push({path: '/welcome'})
            } else {
              const message = get(data, 'error') || get(data, 'message') || 'Authentication failed'
              this.reportError(message)
            }
          },
          error => {
            this.reportError(error)
          }
        ).finally(() => {
          this.isLoggingIn = false
        })
      } else if (uid) {
        this.reportError('Password required')
      } else {
        this.reportError('Both UID and password are required', 'basic-auth-password')
      }
    },
    reportError(message, putFocus='basic-auth-uid') {
      this.devAuthError = typeof message === 'string' ? message : get(message, 'message')
      this.alertScreenReader(this.devAuthError || 'Uh oh, an error occurred.')
      putFocusNextTick(putFocus)
    },
    toCasLogin() {
      getCasLoginURL().then(data => {
        window.location.href = data.casLoginUrl
      })
    }
  }
}
</script>

<style scoped>
.dev-auth-error {
  width: 300px !important;
}
.text-field {
  background-color: white;
  opacity: 0.7;
  width: 300px !important;
}
</style>
