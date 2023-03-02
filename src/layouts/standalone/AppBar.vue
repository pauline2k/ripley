<template>
  <v-app-bar flat>
    <v-app-bar-title>
      <div class="align-center d-flex flex-wrap justify-space-between">
        <div class="me-auto">
          <BuildSummary />
        </div>
        <div v-if="currentUser.isAuthenticated" class="pr-2">
          <v-text-field
            id="update-canvas-course-id"
            v-model="canvasCourseId"
            append-inner-icon="mdi-arrow-right-circle-outline"
            density="compact"
            :disabled="isUpdatingCanvasCourseId"
            hide-details
            label="Canvas Course ID"
            maxlength="12"
            style="width: 200px"
            @click:append-inner="updateCanvasCourseId"
            @keydown.enter="updateCanvasCourseId"
          />
        </div>
        <div class="float-right mr-3 text-body-2">
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
import {logOut, updateUserSession} from '@/api/auth'
import {useContextStore} from '@/stores/context'

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
  data: () => ({
    canvasCourseId: undefined,
    isUpdatingCanvasCourseId: false
  }),
  created() {
    this.canvasCourseId = this.currentUser.canvasCourseId
  },
  methods: {
    logOut() {
      logOut().then(data => window.location.href = data.casLogoutUrl)
    },
    moment,
    updateCanvasCourseId() {
      if (this.currentUser.isAuthenticated) {
        this.isUpdatingCanvasCourseId = true
        updateUserSession(this.canvasCourseId).then(data => {
          useContextStore().setCurrentUser(data)
          this.canvasCourseId = this.currentUser.canvasCourseId
          this.isUpdatingCanvasCourseId = false
          this.$eventHub.emit('current-user-update')
        })
      }
    }
  }
}
</script>
