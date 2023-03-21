<template>
  <v-alert
    v-if="errorMessage || successMessage"
    class="ma-2"
    :closable="closable"
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
    closable: {
      required: false,
      type: Boolean
    },
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
