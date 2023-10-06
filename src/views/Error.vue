<template>
  <AppBar  v-if="!$isInIframe" />
  <v-container
    v-if="!isLoading"
    class="background-splash"
    fill-height
    fluid
  >
    <v-card
      class="elevation-1 mx-auto text-center"
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
        <Header1 :text="header" />
      </v-card-title>
      <v-card-text>
        <div
          id="error-message"
          aria-atomic="true"
          aria-live="polite"
          role="alert"
        >
          {{ applicationState.message }}
          <div v-if="applicationState.stacktrace" class="py-3">
            <pre>{{ applicationState.stacktrace }}</pre>
          </div>
        </div>
      </v-card-text>
      <v-card-subtitle class="mb-7">
        <ContactUsPrompt />
      </v-card-subtitle>
    </v-card>
  </v-container>
</template>

<script>
import AppBar from '@/layouts/standalone/AppBar.vue'
import Context from '@/mixins/Context'
import ContactUsPrompt from '@/components/utils/ContactUsPrompt'
import Header1 from '@/components/utils/Header1.vue'
import {useContextStore} from '@/stores/context'

export default {
  name: 'Error',
  mixins: [Context],
  components: {AppBar, ContactUsPrompt, Header1},
  data: () => ({
    header: undefined
  }),
  created() {
    let url = new URL(window.location.href)
    const error = url.searchParams.get('error')
    const isError = !!error || this.$route.path.includes('error')
    const show404 = !isError && [200, 404].includes(this.applicationState.status)
    useContextStore().setApplicationState(
      this.applicationState.status,
      error || this.applicationState.message
    )
    this.header = show404 ? 'Page Not Found' : 'Uh oh, there was a problem.'
    this.$ready()
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
