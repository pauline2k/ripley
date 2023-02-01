<template>
  <v-container fluid>
    <v-row class="ml-4 mt-4 pt-4">
      <v-col>
        <div class="d-flex">
          <div class="pr-3 pt-2">
            <v-icon class="text-warning" icon="exclamation-triangle" size="2x" />
          </div>
          <div>
            <h1 class="cc-text-xl text-secondary">Page Not Found</h1>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row class="cc-text-big ml-4 mt-4 pb-5">
      <v-col>
        <span id="error-message" aria-live="polite" role="alert">
          <span v-if="$route.redirectedFrom">
            The requested URL {{ this.$route.redirectedFrom }} was not found.
          </span>
          <span v-if="!$route.redirectedFrom">
            Page not found.
          </span>
          If you need assistance then please <a id="contact-us" href="https://dls.berkeley.edu/services/bcourses-0" target="_blank">contact us</a>.
        </span>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'NotFound',
  mounted() {
    this.$ready('404')
  }
}
</script>
