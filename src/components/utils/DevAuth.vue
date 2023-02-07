<template>
  <div class="w-50">
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
      @click="devAuth"
    >
      Dev Auth
    </v-btn>
  </div>
</template>

<script>
import auth from '@/auth'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {devAuthLogIn} from '@/api/auth'
import {app} from '@/main'

export default {
  name: 'DevAuth',
  mixins: [Context, Utils],
  data: () => ({
    error: undefined,
    uid: undefined,
    password: undefined,
    showError: false
  }),
  methods: {
    devAuth() {
      let uid = this.$_.trim(this.uid)
      let password = this.$_.trim(this.password)
      if (uid && password) {
        devAuthLogIn(uid, password).then(
          data => {
            if (data.isAuthenticated) {
              app.config.globalProperties.$currentUser = data
              this.$announcer.polite('You are logged in.')
              this.$router.push({path: data.isAdmin ? '/jobs' : '/welcome'})
            } else {
              const message = this.$_.get(data, 'response.data.error') || this.$_.get(data, 'response.data.message') || this.$_.get(data, 'message') || 'Authentication failed'
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
