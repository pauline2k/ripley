<template>
  <v-menu>
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
import Utils from '@/mixins/Utils.vue'
import {logOut} from '@/api/auth'

export default {
  name: 'AppBarMenu',
  mixins: [Context, Utils],
  data: () => ({
    options: []
  }),
  created() {
    this.options = [
      {
        id: 'my-profile',
        label: 'My Profile',
        onClick: () => {
          this.goToPath(`/profile/${this.currentUser.uid}`)
        }
      },
      {
        id: 'log-out',
        label: 'Log Out',
        onClick: this.logOut
      }
    ]
  },
  methods: {
    logOut() {
      logOut().then(data => window.location.href = data.casLogoutUrl)
    },
  }
}
</script>
