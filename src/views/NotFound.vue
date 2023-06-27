<template>
  <v-app>
    <DefaultBar />
    <v-main>
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
              <v-card-title>
                {{ isError ? 'Error' : 'Page Not Found' }}
              </v-card-title>
              <v-card-text>
                <div v-if="isError">
                  <span
                    id="error-message"
                    aria-live="polite"
                    role="alert"
                  >
                    {{ applicationState.message || 'Uh oh, there was a problem.' }}
                    <div v-if="applicationState.stacktrace" class="py-3">
                      <pre>{{ applicationState.stacktrace }}</pre>
                    </div>
                  </span>
                </div>
                <div
                  v-if="!isError"
                  id="page-not-found"
                  aria-live="polite"
                  role="alert"
                >
                  <span v-if="$route.redirectedFrom">
                    The requested URL {{ $route.redirectedFrom }} was not found.
                  </span>
                  <span v-if="!$route.redirectedFrom">
                    Page not found.
                  </span>
                </div>
              </v-card-text>
              <v-card-subtitle class="pb-5">
                <ContactUsPrompt />
              </v-card-subtitle>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import DefaultBar from '@/layouts/standalone/AppBar.vue'
import derelictOnAlienPlanet from '@/assets/images/derelict-on-alien-planet.jpg'
</script>

<script>
import Context from '@/mixins/Context'
import ContactUsPrompt from '@/components/utils/ContactUsPrompt'

export default {
  name: 'NotFound',
  mixins: [Context],
  components: {ContactUsPrompt},
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
