<template>
  <v-container
    class="background-splash"
    fill-height
    fluid
    :style="{backgroundImage: `url(${nostromoCrew})`}"
  >
    <v-row>
      <v-col>
<!--        <div>-->
<!--          <v-btn-->
<!--            id="sign-in-button"-->
<!--            class="cc-button-blue text-nowrap"-->
<!--            variant="text"-->
<!--            @click="toCasLogin"-->
<!--          >-->
<!--            Sign In-->
<!--          </v-btn>-->
<!--        </div>-->
        <div v-if="$config.devAuthEnabled && !$currentUser.isAuthenticated">
          <h4 class="sr-only">DevAuth</h4>
          <DevAuth />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import nostromoCrew from '@/assets/nostromo-crew-eating-breakfast.png'
</script>

<script>
import Context from '@/mixins/Context'
import DevAuth from '@/components/utils/DevAuth'

export default {
  name: 'Login',
  mixins: [Context],
  components: {DevAuth},
  setup() {
    const showDevAuth = false
    return { showDevAuth }
  },
  methods: {
    toCasLogin() {
      window.location.href = `${this.$config.apiBaseUrl}/auth/cas`
    }
  },
  created() {
    this.$ready('Welcome. Please log in.')
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
