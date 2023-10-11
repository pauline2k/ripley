<template>
  <v-alert
    aria-live="assertive"
    color="red-lighten-2"
    density="compact"
  >
    <div class="align-center d-flex">
      <div class="mr-1">
        <v-icon :icon="mdiAlertCircle" />
      </div>
      <div class="text-white">
        {{ text }}
      </div>
    </div>
  </v-alert>
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
