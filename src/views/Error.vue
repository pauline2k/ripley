<template>
  <div>
    <AppBar v-if="!isInIframe" />
    <v-container
      v-if="!contextStore.isLoading"
      id="content"
      class="background-splash"
      fill-height
      fluid
    >
      <v-card
        class="elevation-1 mt-12 mx-auto text-center"
        :max-width="contextStore.applicationState.stacktrace ? '40rem' : '30rem'"
        outlined
      >
        <v-img
          v-if="!isInIframe"
          alt="TV screen with colored bars"
          aria-label="TV screen with colored bars"
          :aspect-ratio="16 / 9"
          src="@/assets/images/color-bars.png"
        />
        <v-card-title>
          <Header1 class="mt-8 text-wrap" :text="header" />
        </v-card-title>
        <v-card-text>
          <div id="error-message">
            <span aria-live="polite">{{ message }}</span>
            <div v-if="stacktrace" class="px-5 py-3 text-left text-sm-caption">
              <pre>{{ stacktrace }}</pre>
            </div>
          </div>
          <ContactUsPrompt class="mb-5" />
        </v-card-text>
      </v-card>
    </v-container>
  </div>
</template>

<script setup>
import {get} from 'lodash'
import {onMounted, ref} from 'vue'
import {useRoute} from 'vue-router'
import AppBar from '@/layouts/standalone/AppBar.vue'
import ContactUsPrompt from '@/components/utils/ContactUsPrompt'
import Header1 from '@/components/utils/Header1.vue'
import {isInIframe} from '@/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const header = ref()
const message = ref()
const stacktrace = ref()

onMounted(() => {
  const params = new URL(window.location.href).searchParams
  header.value = params.get('h') || getDefaultHeader()
  const body = params.get('m') || contextStore.applicationState.message
  message.value = header.value === body ? null : body
  stacktrace.value = contextStore.applicationState.stacktrace
  contextStore.loadingComplete()
})

const getDefaultHeader = () => {
  const status = get(useRoute().meta, 'is404') ? 404 : contextStore.applicationState.status
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
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  white-space: -moz-pre-wrap;
  white-space: -o-pre-wrap;
  word-wrap: break-word;
}
</style>
