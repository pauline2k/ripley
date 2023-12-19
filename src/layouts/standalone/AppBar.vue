<template>
  <v-app-bar class="display-none-when-print pr-3" flat>
    <v-app-bar-title>
      <div class="align-center d-flex flex-wrap justify-space-between">
        <div class="me-auto">
          <BuildSummary />
        </div>
        <div class="float-right pr-3 text-body-2">
          <AppBarMenu v-if="currentUser.isAuthenticated" />
          <span v-if="!currentUser.isAuthenticated">
            Berkeley &copy; {{ new Date().getFullYear() }} UC Regents
          </span>
        </div>
      </div>
    </v-app-bar-title>
  </v-app-bar>
</template>

<script setup>
import AppBarMenu from '@/components/utils/AppBarMenu.vue'
import BuildSummary from '@/components/utils/BuildSummary'
</script>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'AppBar',
  mixins: [Context],
  props: {
    includeBuildSummary: {
      required: false,
      type: Boolean
    }
  }
}
</script>
