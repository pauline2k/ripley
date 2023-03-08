<template>
  <v-progress-circular
    class="mr-2"
    :color="color"
    indeterminate
    size="x-small"
    width="3"
  />
</template>

<script>
export default {
  name: 'SpinnerWithinButton',
  props: {
    color: {
      default: 'white',
      type: String,
      required: false
    }
  }
}
</script>
