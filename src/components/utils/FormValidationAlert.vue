<template>
  <v-alert
    aria-live="assertive"
    color="red-lighten-2"
    density="compact"
  >
    <div class="align-center d-flex">
      <div class="mr-1">
        <v-icon icon="mdi-alert-circle" />
      </div>
      <div class="text-white">
        {{ text }}
      </div>
    </div>
  </v-alert>
</template>

<script lang="ts">
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
