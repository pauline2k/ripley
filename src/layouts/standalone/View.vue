<template>
  <v-main>
    <PageLoadProgress v-if="isLoading" />
    <router-view />
  </v-main>
</template>

<script>
import Context from '@/mixins/Context'
import PageLoadProgress from '@/components/utils/PageLoadProgress'

export default {
  name: 'Jobs',
  components: {PageLoadProgress},
  mixins: [Context]
}
</script>
