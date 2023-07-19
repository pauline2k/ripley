<template>
  <AppBar />
  <router-view />
</template>

<script>
import Context from '@/mixins/Context'
import AppBar from './AppBar.vue'

export default {
  name: 'BaseStandalone',
  components: {AppBar},
  mixins: [Context]
}
</script>
