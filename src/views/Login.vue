<template>
  <v-container
    class="background-splash"
    fill-height
    fluid
    :style="{backgroundImage: `url(${nostromoCrew})`}"
  >
    <v-row>
      <v-col v-if="!$currentUser.isAuthenticated">
        <div>
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
        <div v-if="$config.devAuthEnabled">
          <h4 class="sr-only">DevAuth</h4>
          <DevAuth />
        </div>
      </v-col>
    </v-row>
    <v-col v-if="$currentUser.isAuthenticated">
      Hello! {{ $currentUser }}
    </v-col>
  </v-container>
</template>

<script setup>
import nostromoCrew from '@/assets/nostromo-crew-eating-breakfast.png'
</script>

<script>
import Context from '@/mixins/Context'
import DevAuth from '@/components/utils/DevAuth'
import {getCasLoginURL} from '@/api/auth'

export default {
  name: 'Login',
  mixins: [Context],
  components: {DevAuth},
  setup() {
    const showDevAuth = false
    this.$ready('Welcome. Please log in.')
    return {showDevAuth}
  },
  methods: {
    toCasLogin() {
      getCasLoginURL().then(data => {
        console.log(data)
        window.location.href = data.casLoginUrl
      })
    }
  }
}
</script>

<style scoped>
button {
  height: 48px;
  width: 200px;
}
h1 {
  color: #025a86;
  font-size: 23px;
  font-weight: bold;
  margin: 0 0 10px;
}
.background-splash {
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  min-height: 100vh;
}
</style>
