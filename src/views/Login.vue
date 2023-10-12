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
        <div v-if="config.devAuthEnabled">
          <h2 class="sr-only">DevAuth</h2>
          <DevAuth />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import DevAuth from '@/components/utils/DevAuth'
import Header1 from '@/components/utils/Header1.vue'
import nostromoCrew from '@/assets/images/nostromo-crew-eating-breakfast.png'
</script>

<script>
import Context from '@/mixins/Context'
import {getCasLoginURL} from '@/api/auth'

export default {
  name: 'Login',
  mixins: [Context],
  created() {
    const showDevAuth = false
    this.$ready()
    return {showDevAuth}
  },
  methods: {
    toCasLogin() {
      getCasLoginURL().then(data => {
        window.location.href = data.casLoginUrl
      })
    }
  }
}
</script>
