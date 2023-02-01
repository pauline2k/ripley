<template>
  <v-container class="pl-0 pr-0" fluid>
    <v-row class="mb-2 mt-4" no-gutters>
      <v-col class="pl-3">
        <h1 class="cc-text-xl text-secondary">{{ $currentUser.firstName }}'s Toolbox</h1>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'Toolbox',
  created() {
    this.$ready('Toolbox')
  }
}
</script>
