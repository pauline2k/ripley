<template>
  <v-progress-circular
    v-if="true || $isInIframe"
    class="spinner"
    :size="50"
    color="primary"
    indeterminate
  />
</template>

<script>
export default {
  name: 'PageLoadProgress'
}
</script>

<style scoped>
.spinner {
  bottom: 0;
  height: 2em;
  left: 0;
  margin: auto;
  overflow: show;
  position: fixed;
  right: 0;
  top: 0;
  width: 2em;
  z-index: 999;
}
</style>
