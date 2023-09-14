<template>
  <div class="w-50">
    <div class="pb-2 pt-5">
      <v-text-field
        id="basic-auth-uid"
        v-model="uid"
        :aria-invalid="!!error"
        class="text-field"
        :disabled="isLoggingIn"
        hide-details
        label="UID"
        required
        variant="outlined"
        @keydown.enter="devAuth"
      />
    </div>
    <div class="pb-2">
      <v-text-field
        id="basic-auth-password"
        v-model="password"
        autocomplete="off"
        class="my-2 text-field"
        :disabled="isLoggingIn"
        :error-messages="error"
        hide-details
        label="Password"
        required
        type="password"
        variant="outlined"
        @keydown.enter="devAuth"
      />
    </div>
    <div class="pb-4">
      <v-text-field
        id="basic-auth-canvas-course-id"
        v-model="canvasSiteId"
        :aria-invalid="!!error"
        class="text-field"
        :disabled="isLoggingIn"
        hide-details
        label="Canvas Course ID (optional)"
        required
        variant="outlined"
        @keydown.enter="devAuth"
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
</template>

<script>
import Context from '@/mixins/Context'
import {devAuthLogIn} from '@/api/auth'
import {get, trim} from 'lodash'
import {useContextStore} from '@/stores/context'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'DevAuth',
  mixins: [Context],
  data: () => ({
    canvasSiteId: undefined,
    error: undefined,
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
  methods: {
    devAuth() {
      const canvasSiteId = trim(this.canvasSiteId)
      const password = trim(this.password)
      const uid = trim(this.uid)
      if (uid && password) {
        this.isLoggingIn = true
        devAuthLogIn(canvasSiteId, uid, password).then(
          data => {
            if (data.isAuthenticated) {
              useContextStore().setCurrentUser(data)
              this.$announcer.polite('You are logged in.')
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
      this.error = typeof message === 'string' ? message : get(message, 'message')
      this.$announcer.polite(this.error || 'Uh oh, an error occurred.')
      putFocusNextTick(putFocus)
    }
  }
}
</script>

<style>
.text-field {
  background-color: white;
  opacity: 0.7;
}
</style>
