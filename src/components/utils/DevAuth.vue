<template>
  <div class="w-50 pt-5">
    <v-text-field
      id="basic-auth-canvas-course-id"
      v-model="canvasCourseId"
      :aria-invalid="!!error"
      class="mb-1 text-field"
      hide-details
      label="Canvas Course ID"
      required
      variant="outlined"
      @keydown.enter="devAuth"
    />
    <v-text-field
      id="basic-auth-uid"
      v-model="uid"
      :aria-invalid="!!error"
      class="mb-1 text-field"
      hide-details
      label="UID"
      required
      variant="outlined"
      @keydown.enter="devAuth"
    />
    <v-text-field
      id="basic-auth-password"
      v-model="password"
      autocomplete="off"
      class="mb-1 text-field"
      :error-messages="error"
      hide-details
      label="Password"
      required
      type="password"
      variant="outlined"
      @keydown.enter="devAuth"
    />
    <v-btn
      id="basic-auth-submit-button"
      :disabled="disableSubmit"
      @click="devAuth"
    >
      Dev Auth
    </v-btn>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {devAuthLogIn} from '@/api/auth'
import {useContextStore} from '@/stores/context'

export default {
  name: 'DevAuth',
  mixins: [Context, Utils],
  data: () => ({
    canvasCourseId: undefined,
    error: undefined,
    password: undefined,
    showError: false,
    uid: undefined
  }),
  computed: {
    disableSubmit() {
      return !this.$_.trim(this.canvasCourseId) || !this.$_.trim(this.password) || !this.$_.trim(this.uid)
    }
  },
  methods: {
    devAuth() {
      const canvasCourseId = this.$_.trim(this.canvasCourseId)
      const password = this.$_.trim(this.password)
      const uid = this.$_.trim(this.uid)
      if (canvasCourseId && uid && password) {
        devAuthLogIn(canvasCourseId, uid, password).then(
          data => {
            if (data.isAuthenticated) {
              useContextStore().setCurrentUser(data)
              this.$announcer.polite('You are logged in.')
              this.$router.push({path: '/welcome'})
            } else {
              const message = this.$_.get(data, 'error') || this.$_.get(data, 'message') || 'Authentication failed'
              this.reportError(message)
            }
          },
          error => {
            this.reportError(error)
          }
        )
      } else if (uid) {
        this.reportError('Password required')
      } else {
        this.reportError('Both UID and password are required', 'basic-auth-password')
      }
    },
    reportError(message, putFocus='basic-auth-uid') {
      this.error = this.$_.get(message, 'message')
      this.$announcer.polite(this.error)
      this.$putFocusNextTick(putFocus)
    }
  }
}
</script>

<style>
.text-field {
  background-color: white;
  opacity: 0.5;
}
</style>
