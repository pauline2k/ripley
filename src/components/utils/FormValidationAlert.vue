<template>
  <div aria-live="assertive" role="alert">
    <v-alert
      v-if="show"
      class="mb-2"
      density="compact"
      :icon="mdiAlertCircle"
      role="none"
      :text="text"
      type="error"
    />
  </div>
</template>

<script setup>
import {mdiAlertCircle} from '@mdi/js'
</script>

<script>
export default {
  name: 'FormValidationAlert',
  props: {
    show: {
      required: true,
      type: Boolean
    },
    text: {
      required: true,
      type: String
    }
  }
}
</script>
