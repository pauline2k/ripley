<template>
  <v-progress-circular
    aria-valuetext="in progress"
    class="mr-2"
    :color="color"
    indeterminate
    role="progressbar"
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
