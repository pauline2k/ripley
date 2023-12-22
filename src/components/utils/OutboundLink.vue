<template>
  <a
    :id="id || `link-to-${href.replace(/\W/g, '')}`"
    :href="href"
    target="_blank"
    :title="title"
  >
    <slot />
    <v-icon
      v-if="!hideIcon"
      class="ml-1"
      :icon="mdiOpenInNew"
      size="x-small"
    />
    <span class="sr-only print-hide"> (link opens new browser tab)</span>
  </a>
</template>

<script setup>
import {mdiOpenInNew} from '@mdi/js'
</script>

<script>
export default {
  name: 'OutboundLink',
  props: {
    hideIcon: {
      type: Boolean,
      required: false
    },
    href: {
      type: String,
      required: true
    },
    id: {
      default: undefined,
      type: String,
      required: false
    },
    title: {
      default: undefined,
      type: String,
      required: false
    }
  }
}
</script>
