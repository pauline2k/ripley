<template>
  <v-app>
    <DefaultBar />
    <v-main class="v-main-when-print">
      <PageLoadProgress v-if="isLoading" />
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import Context from '@/mixins/Context'
import DefaultBar from './AppBar.vue'
import PageLoadProgress from '@/components/utils/PageLoadProgress'

export default {
  name: 'BaseStandalone',
  components: {DefaultBar, PageLoadProgress},
  mixins: [Context]
}
</script>
