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
      v-if="!hideIcon"
      class="ml-1r"
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
