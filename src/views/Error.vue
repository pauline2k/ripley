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
            <h2>{{ header }}</h2>
          </v-card-title>
          <v-card-text>
            <div
              id="error-message"
              aria-live="polite"
              class="ml-2"
              role="alert"
            >
              {{ applicationState.message }}
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
import {useContextStore} from '@/stores/context'

export default {
  name: 'Error',
  mixins: [Context],
  components: {AppBar, ContactUsPrompt},
  data: () => ({
    header: undefined
  }),
  mounted() {
    let url = new URL(window.location.href)
    const error = url.searchParams.get('error')
    const show404 = !error && [200, 404].includes(this.applicationState.status)
    const message = error || this.applicationState.message
    useContextStore().setApplicationState(show404 ? 404 : 500, message)
    this.header = show404 ? 'Page Not Found' : (message ? 'Error' : 'Uh oh, there was a problem.')
    this.$ready(this.header)
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
