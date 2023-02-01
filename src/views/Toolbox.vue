<template>
  <v-container class="pl-0 pr-0" fluid>
    <ToolboxHeader />
    <v-row class="mb-2 mt-4" no-gutters>
      <v-col class="pl-3">
        <h1 class="cc-text-xl text-secondary">{{ $currentUser.firstName }}'s Toolbox</h1>
      </v-col>
    </v-row>
    <v-row v-if="canViewAs || this.$currentUser.canAdministerOec">
      <v-col v-if="canViewAs" sm="6">
        <ActAs />
      </v-col>
      <v-col v-if="this.$currentUser.canAdministerOec" sm="6">
        <Oec />
      </v-col>
    </v-row>
    <v-row v-if="!canViewAs && !this.$currentUser.canAdministerOec">
      <v-col sm="12">
        <div class="text-center">
          <img class="w-50" src="@/assets/conjunction-junction.jpg" alt="Image of train junction" />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ToolboxHeader from '@/components/toolbox/ToolboxHeader'

export default {
  name: 'Toolbox',
  components: {ToolboxHeader},
  data: () => ({
    canViewAs: undefined
  }),
  created() {
    this.canViewAs = this.$currentUser.isDirectlyAuthenticated && this.$currentUser.canViewAs
    this.$ready('Toolbox')
  }
}
</script>
