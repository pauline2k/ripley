<template>
  <div>
    <AppBar />
    <router-view id="content" tabindex="-1" />
  </div>
</template>

<script lang="ts" setup>
import AppBar from '@/layouts/standalone/AppBar.vue'
</script>
