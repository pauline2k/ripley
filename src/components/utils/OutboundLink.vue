<template>
  <a
    :id="id || `link-to-${href.replace(/\W/g, '')}`"
    class="align-end d-inline-block text-pretty-wrap"
    :href="href"
    target="_blank"
    :title="title"
  >
    <span class="text-wrap">
      <slot />
    </span>
    <v-icon
      v-if="!hideIcon"
      class="ml-2r"
      :icon="mdiOpenInNew"
      size="x-small"
    />
    <span class="sr-only print-hide"> (opens in new tab)</span>
  </a>
</template>

<script lang="ts" setup>
import {mdiOpenInNew} from '@mdi/js'

defineProps({
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
})
</script>
