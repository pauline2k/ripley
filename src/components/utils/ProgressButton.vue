<template>
  <v-btn
    :id="id"
    :aria-label="ariaLabel"
    :color="color"
    :disabled="disabled"
    :prepend-icon="inProgress ? undefined : prependIcon"
    :size="size"
    :variant="variant"
    @click.prevent="action"
  >
    <div class="align-center d-flex text-no-wrap">
      <v-progress-circular
        v-if="inProgress"
        class="mr-2"
        indeterminate
        size="x-small"
        width="3"
      />
      <div>
        <slot>
          {{ text }}
        </slot>
      </div>
    </div>
  </v-btn>
</template>

<script setup>
defineProps({
  action: {
    type: Function,
    required: true
  },
  ariaLabel: {
    default: undefined,
    type: String,
    required: false
  },
  color: {
    default: 'primary',
    type: String,
    required: false
  },
  disabled: {
    type: Boolean,
    required: false
  },
  id: {
    type: String,
    required: true
  },
  inProgress: {
    type: Boolean,
    required: false
  },
  prependIcon: {
    default: undefined,
    type: String,
    required: false
  },
  size: {
    default: 'default',
    type: [String, Number],
    required: false
  },
  text: {
    default: undefined,
    type: String,
    required: false
  },
  variant: {
    default: 'flat',
    type: String,
    required: false
  }
})
</script>
