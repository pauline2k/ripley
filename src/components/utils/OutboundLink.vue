<template>
  <a
    :id="id || `link-to-${href.replace(/\W/g, '')}`"
    :href="href"
    target="_blank"
    :title="title"
  >
    <div class="align-center d-flex">
      <div>
        <slot />
      </div>
      <div>
        <v-icon class="ml-1" :icon="mdiOpenInNew" size="small" />
        <span class="sr-only print-hide"> (link opens new browser tab)</span>
      </div>
    </div>
  </a>
</template>

<script setup>
import {mdiOpenInNew} from '@mdi/js'
</script>

<script>
export default {
  name: 'OutboundLink',
  props: {
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
