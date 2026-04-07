<template>
  <v-app-bar class="display-none-when-print pr-3" flat>
    <v-app-bar-title>
      <div class="align-center d-flex flex-wrap justify-space-between">
        <div class="me-auto">
          <BuildSummary />
        </div>
        <div class="ml-auto pr-3 text-body-2">
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
import {useContextStore} from '@/stores/context'

defineProps({
  includeBuildSummary: {
    required: false,
    type: Boolean
  }
})

const currentUser = useContextStore().currentUser
</script>
