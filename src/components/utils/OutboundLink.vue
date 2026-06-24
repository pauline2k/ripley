<template>
  <a
    :id="id || `link-to-${href.replace(/\W/g, '')}`"
    :class="['align-end d-inline-block', noWrap ? 'text-no-wrap' : 'text-pretty-wrap', {'with-terminating-period': periodTerminated}]"
    :href="href"
    target="_blank"
    :title="title"
  >
    <span :class="['text-decoration-underline', noWrap ? 'text-no-wrap' : 'text-wrap']">
      <slot>
        {{ text }}
      </slot>
    </span>
    <v-icon
      class="d-print-none ml-1r"
      :icon="icon"
      size="x-small"
    />
    <span class="d-print-none sr-only"> (opens in new tab)</span>
  </a>
</template>

<script lang="ts" setup>
import {mdiOpenInNew} from '@mdi/js'

defineProps({
  href: {
    type: String,
    required: true
  },
  icon: {
    default: mdiOpenInNew,
    type: String,
    required: false
  },
  id: {
    default: undefined,
    type: String,
    required: false
  },
  noWrap: {
    type: Boolean,
    required: false
  },
  periodTerminated: {
    type: Boolean,
    required: false
  },
  text: {
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

<style lang="scss" scoped>
.with-terminating-period {
  text-decoration: none !important;
  &::after {
    content: ".";
  }
}
</style>
