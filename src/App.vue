<template>
  <v-app>
    <div v-if="!isInIframe">
      <a
        id="skip-to-content-link"
        href="#content"
        class="sr-only sr-only-focusable"
        tabindex="0"
      >
        Skip to content
      </a>
    </div>
    <v-main id="ripley-main" class="v-main-when-print">
      <div
        id="announcer"
        :role="announcerRole"
        :aria-live="context.screenReaderAlert.politeness"
        aria-atomic="true"
        class="sr-only"
      >
        {{ context.screenReaderAlert.message }}
      </div>
      <PageLoadProgress v-if="context.isLoading" />
      <router-view v-if="context.applicationState.status === 200" />
      <Error v-if="context.applicationState.status !== 200" />
    </v-main>
  </v-app>
</template>

<script setup>
import {computed} from 'vue'
import Error from '@/views/Error'
import PageLoadProgress from '@/components/utils/PageLoadProgress.vue'
import {isInIframe} from '@/utils'
import {useContextStore} from '@/stores/context'

const context = useContextStore()
const announcerRole = computed(() =>
  context.screenReaderAlert.politeness === 'assertive' ? 'alert' : 'status'
)
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type -->
<style lang="scss">
.alert {
  background-color: $color-alert-background;
  border: 0;
  border-radius: 3px;
  color: $color-alert-foreground;
  font-size: 0.875rem;
  font-weight: normal;
  margin: 10px 0;
  padding: 8px 15px 8px 14px;
  text-shadow: 0 1px 0 $color-white-translucent;
}
.alert-info {
  background-color: $color-alert-info-background;
  color: $color-alert-info-foreground;
}
.alert-success {
  background-color: $color-alert-success-background;
  color: $color-alert-success-foreground;
}
.alert-error {
  background-color: $color-alert-error-background;
  color: $color-alert-error-foreground;
}
.icon-red {
  color: $color-harley-davidson-orange;
}
.validation-messages {
  color: $color-harley-davidson-orange;
  font-size: 0.875rem;
  font-weight: 500;
  min-height: 20px;
  margin: 0 12px 4px;
}
</style>
