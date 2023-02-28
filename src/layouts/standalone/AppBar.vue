<template>
  <v-app-bar flat>
    <v-app-bar-title>
      <div class="align-center d-flex justify-space-between">
        <div>
          <BuildSummary />
        </div>
        <div class="float-right mr-3 text-body-2" cols="6">
          <v-menu v-if="currentUser.isAuthenticated">
            <template #activator="{ props }">
              <v-btn
                color="primary"
                v-bind="props"
              >
                {{ currentUser.firstName }}
              </v-btn>
            </template>
            <v-list>
              <v-list-item>
                <v-btn
                  id="log-out"
                  variant="plain"
                  @click="logOut"
                >
                  Log out
                </v-btn>
              </v-list-item>
            </v-list>
          </v-menu>
          <span v-if="!currentUser.isAuthenticated">
            Berkeley &copy; {{ new Date().getFullYear() }} UC Regents
          </span>
        </div>
      </div>
    </v-app-bar-title>
  </v-app-bar>
</template>

<script>
import BuildSummary from '@/components/utils/BuildSummary'
import Context from '@/mixins/Context'
import moment from 'moment'
import {logOut} from '@/api/auth'

export default {
  name: 'AppBar',
  mixins: [Context],
  components: {BuildSummary},
  props: {
    includeBuildSummary: {
      required: false,
      type: Boolean
    }
  },
  methods: {
    logOut() {
      logOut().then(data => window.location.href = data.casLogoutUrl)
    },
    moment
  }
}
</script>
