<template>
  <AppBar  v-if="!$isInIframe" />
  <v-container
    class="background-splash"
    fill-height
    fluid
    :style="{backgroundImage: `url(${derelictOnAlienPlanet})`}"
  >
    <v-row class="mt-4 pt-4">
      <v-col>
        <v-card
          class="mx-auto"
          :max-width="applicationState.stacktrace ? 640 : 480"
        >
          <v-card-title class="ml-2 mt-3">
            {{ isError ? 'Error' : applicationState.message || 'Page Not Found' }}
          </v-card-title>
          <v-card-text v-if="isError || !applicationState.message">
            <div
              v-if="isError"
              id="error-message"
              aria-live="polite"
              role="alert"
            >
              {{ applicationState.message || 'Uh oh, there was a problem.' }}
              <div v-if="applicationState.stacktrace" class="py-3">
                <pre>{{ applicationState.stacktrace }}</pre>
              </div>
            </div>
          </v-card-text>
          <v-card-subtitle class="ml-2 mb-7">
            <ContactUsPrompt />
          </v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import derelictOnAlienPlanet from '@/assets/images/derelict-on-alien-planet.jpg'
</script>

<script>
import AppBar from '@/layouts/standalone/AppBar.vue'
import Context from '@/mixins/Context'
import ContactUsPrompt from '@/components/utils/ContactUsPrompt'

export default {
  name: 'NotFound',
  mixins: [Context],
  components: {AppBar, ContactUsPrompt},
  data: () => ({
    isError: false
  }),
  mounted() {
    this.isError = ![200, 404].includes(this.applicationState.status)
    this.$ready(this.isError ? 'Error' : 'Page Not Found')
  }
}
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  white-space: -moz-pre-wrap;
  white-space: -o-pre-wrap;
  word-wrap: break-word;
}
</style>
