<template>
  <v-alert
    v-if="errorMessage || successMessage"
    class="mb-2"
    closable
    density="compact"
    role="alert"
    :type="errorMessage ? 'warning' : 'successMessage'"
  >
    {{ errorMessage || successMessage }}
  </v-alert>
</template>

<script>
export default {
  name: 'Alert',
  props: {
    errorMessage: {
      default: undefined,
      required: false,
      type: String
    },
    successMessage: {
      default: undefined,
      required: false,
      type: String
    }
  }
}
</script>
