<template>
  <div aria-live="assertive" role="alert">
    <v-alert
      v-if="show"
      class="mb-2"
      density="compact"
      :icon="mdiAlertCircle"
      icon-size="1rem"
      role="none"
      :text="text"
      type="error"
      variant="tonal"
    />
  </div>
</template>

<script setup>
import {mdiAlertCircle} from '@mdi/js'

defineProps({
  show: {
    required: true,
    type: Boolean
  },
  text: {
    required: true,
    type: String
  }
})
</script>
