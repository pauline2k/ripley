<template>
  <v-progress-circular
    class="margin-right"
    :color="color"
    indeterminate
    :size="size"
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
    },
    size: {
      default: 'x-small',
      type: [Number, String],
      required: false
    }
  }
}
</script>

<style scoped>
.margin-right {
  margin-right: 4px;
}
</style>
