<template>
  <AppBar v-if="!$isInIframe" />
  <v-container
    v-if="!isLoading"
    id="content"
    class="background-splash"
    fill-height
    fluid
  >
    <v-card
      class="elevation-1 mt-12 mx-auto text-center"
      :max-width="applicationState.stacktrace ? 640 : 480"
      outlined
    >
      <v-img
        v-if="!$isInIframe"
        alt="TV screen with colored bars"
        aria-label="TV screen with colored bars"
        :aspect-ratio="16 / 9"
        src="@/assets/images/color-bars.png"
      />
      <v-card-title>
        <Header1 class="mt-8" :text="header" />
      </v-card-title>
      <v-card-text>
        <div
          v-if="message || stacktrace"
          id="error-message"
          aria-live="polite"
          role="alert"
        >
          <span v-if="message">{{ message }}</span>
          <div v-if="stacktrace" class="px-5 py-3 text-left text-sm-caption">
            <pre>{{ stacktrace }}</pre>
          </div>
        </div>
        <ContactUsPrompt class="mb-5" />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import AppBar from '@/layouts/standalone/AppBar.vue'
import Context from '@/mixins/Context'
import ContactUsPrompt from '@/components/utils/ContactUsPrompt'
import Header1 from '@/components/utils/Header1.vue'
import {get} from 'lodash'
import {useRoute} from 'vue-router'

export default {
  name: 'Error',
  components: {AppBar, ContactUsPrompt, Header1},
  mixins: [Context],
  data: () => ({
    header: undefined,
    message: undefined,
    stacktrace: undefined
  }),
  created() {
    const params = new URL(window.location.href).searchParams
    this.header = params.get('h') || this.getDefaultHeader()
    const body = params.get('m') || this.applicationState.message
    this.message = this.header === body ? null : body
    this.stacktrace = this.applicationState.stacktrace
    this.$ready()
  },
  methods: {
    getDefaultHeader() {
      const status = get(useRoute().meta, 'is404') ? 404 : this.applicationState.status
      switch(status) {
      case 403: {
        return 'Unauthorized'
      }
      case 404: {
        return 'Page Not Found'
      }
      default: {
        return 'Uh oh, there was a problem.'
      }
      }
    }
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
