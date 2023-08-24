<template>
  <v-menu :disabled="isLoading">
    <template #activator="{ props }">
      <v-btn
        v-bind="props"
        variant="outlined"
      >
        {{ currentUser.firstName || currentUser.uid }}
      </v-btn>
    </template>
    <v-list class="pt-3">
      <v-list-item-action
        v-for="option in options"
        :key="option.id"
      >
        <v-btn
          :id="option.id"
          variant="plain"
          @click="option.onClick"
        >
          {{ option.label }}
        </v-btn>
      </v-list-item-action>
    </v-list>
  </v-menu>
</template>

<script>
import Context from '@/mixins/Context.vue'
import {logOut} from '@/api/auth'

export default {
  name: 'AppBarMenu',
  mixins: [Context],
  data: () => ({
    options: []
  }),
  created() {
    this.options = [
      {
        id: 'my-profile',
        label: 'My Profile',
        onClick: () => {
          this.$router.push({path: `/profile/${this.currentUser.uid}`})
        }
      }
    ]
    if (this.currentUser.canvasSiteId) {
      this.options.push({
        id: 'current-user-canvas-site',
        label: `Canvas Site ${this.currentUser.canvasSiteId}`,
        onClick: () => {
          this.$router.push({path: `/canvas_site/${this.currentUser.canvasSiteId}`})
        }
      })
    }
    this.options.push({
      id: 'log-out',
      label: 'Log Out',
      onClick: this.logOut
    })
  },
  methods: {
    logOut() {
      this.loadingStart()
      logOut().then(data => window.location.href = data.casLogoutUrl)
    },
  }
}
</script>
