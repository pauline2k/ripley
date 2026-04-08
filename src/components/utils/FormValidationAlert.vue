<template>
  <v-alert
    aria-live="assertive"
    density="compact"
    :icon="mdiAlertCircle"
    :text="text"
    type="error"
  />
</template>

<script setup>
import {mdiAlertCircle} from '@mdi/js'
</script>

<script>
export default {
  name: 'FormValidationAlert',
  props: {
    text: {
      required: true,
      type: String
    }
  }
}
</script>
