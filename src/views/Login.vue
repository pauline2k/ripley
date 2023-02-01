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
        <div>
          <img alt="bCourses logo" class="float-left img-fluid" src="@/assets/bcourses_righthand.png">
        </div>
        <div class="pb-5">
          <h1>ETS Support Utilities</h1>
        </div>
      </v-col>
    </v-row>
    <StandaloneFooter :include-build-summary="true" />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import StandaloneFooter from '@/components/utils/StandaloneFooter'

export default {
  name: 'Login',
  mixins: [Context],
  components: {StandaloneFooter},
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
