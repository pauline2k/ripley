<template>
  <div class="cc-page-splash">
    <v-row class="cc-container-main d-flex flex-column-reverse p-3 text-center">
      <v-col sm="12" md="6">
        <div class="pt-5">
          <v-btn
            id="sign-in-button"
            class="cc-button-blue text-nowrap"
            size="lg"
            variant="text"
            @click="toCasLogin"
          >
            Sign In
          </v-btn>
        </div>
        <div v-if="$config.devAuthEnabled && !$currentUser.isAuthenticated" class="pt-2">
          <div class="d-flex pb-2">
            <div>
              <h4>DevAuth</h4>
            </div>
            <div>
              <v-btn
                id="toggle-show-dev-auth"
                aria-controls="dev-auth-collapse"
                variant="text"
                @click="showDevAuth = !showDevAuth"
              >
                <v-icon :icon="showDevAuth ? 'caret-up' : 'caret-down'" />
              </v-btn>
            </div>
          </div>
          <v-expansion-panels v-model="showDevAuth">
            <v-expansion-panel id="dev-auth-collapse">
              <DevAuth />
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
      </v-col>
    </v-row>
    <StandaloneFooter :include-build-summary="true" />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DevAuth from '@/components/utils/DevAuth'
import StandaloneFooter from '@/components/utils/StandaloneFooter'

export default {
  name: 'Login',
  mixins: [Context],
  components: {DevAuth, StandaloneFooter},
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
</style>
