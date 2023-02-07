<template>
  <v-banner class="pa-8">
    <v-icon icon="mdi-alert" color="warning" x-large />
    <div>
      <div class="pb-2">
        <h1 class="sr-only">Error</h1>
        <span id="error-message" aria-live="polite" role="alert">{{ message || 'Uh oh, there was a problem.' }}</span>
      </div>
      <div>
        <ContactUsPrompt />
      </div>
    </div>
  </v-banner>
</template>

<script>
import ContactUsPrompt from '@/components/utils/ContactUsPrompt'

export default {
  name: 'Error',
  components: {ContactUsPrompt},
  data: () => ({
    message: undefined
  }),
  mounted() {
    this.message = this.$route.query.m
    this.$ready('Error')
  }
}
</script>
