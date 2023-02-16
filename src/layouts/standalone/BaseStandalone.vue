<template>
  <v-app>
    <DefaultBar />
    <v-main>
      <PageLoadProgress v-if="isLoading" />
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import DefaultBar from './AppBar.vue'
</script>

<script>
import Context from '@/mixins/Context'
import PageLoadProgress from '@/components/utils/PageLoadProgress'

export default {
  name: 'BaseStandalone',
  components: {PageLoadProgress},
  mixins: [Context]
}
</script>
