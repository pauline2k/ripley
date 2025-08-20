<template>
  <div>
    <AppBar />
    <router-view id="content" />
  </div>
</template>

<script lang="ts" setup>
import AppBar from '@/layouts/standalone/AppBar.vue'
</script>
