<template>
  <a
    :id="id || `link-to-${href.replace(/\W/g, '')}`"
    class="align-end d-inline-block text-pretty-wrap "
    :class="{'with-terminating-period': periodTerminated}"
    :href="href"
    target="_blank"
    :title="title"
  >
    <span class="text-decoration-underline text-wrap">
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
