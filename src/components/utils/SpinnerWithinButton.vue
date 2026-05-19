<template>
  <v-progress-circular
    class="progress-btn-icon"
    :color="color"
    indeterminate
    :size="size"
    width="3"
  />
</template>

<script lang="ts" setup>
defineProps({
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
})
</script>

<style scoped>
.progress-btn-icon {
  margin-bottom: 0.063rem;
  margin-right: 4px;
}
</style>
