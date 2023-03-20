<template>
  <v-app-bar flat>
    <v-app-bar-title>
      <div class="align-center d-flex flex-wrap justify-space-between">
        <div class="me-auto">
          <BuildSummary />
        </div>
        <div v-if="currentUser.isAuthenticated" class="pr-5">
          <v-text-field
            id="update-canvas-course-id"
            v-model="canvasSiteId"
            :append-inner-icon="isUpdatingCanvasSiteId ? 'mdi-progress-check' : 'mdi-arrow-right-circle-outline'"
            density="compact"
            :disabled="isUpdatingCanvasSiteId"
            hide-details
            label="Canvas Course ID"
            maxlength="10"
            :error="!!$_.trim(canvasSiteId) && !isCanvasSiteIdValid"
            style="width: 200px"
            @click:append-inner="updateCanvasSiteId"
            @keydown.enter="updateCanvasSiteId"
          />
        </div>
        <div class="float-right mr-3 text-body-2">
          <AppBarMenu v-if="currentUser.isAuthenticated" />
          <span v-if="!currentUser.isAuthenticated">
            Berkeley &copy; {{ new Date().getFullYear() }} UC Regents
          </span>
        </div>
      </div>
    </v-app-bar-title>
  </v-app-bar>
</template>

<script>
import AppBarMenu from '@/components/utils/AppBarMenu.vue'
import BuildSummary from '@/components/utils/BuildSummary'
import Context from '@/mixins/Context'
import moment from 'moment'
import Utils from '@/mixins/Utils'
import {updateUserSession} from '@/api/auth'
import {useContextStore} from '@/stores/context'

export default {
  name: 'AppBar',
  mixins: [Context, Utils],
  components: {AppBarMenu, BuildSummary},
  props: {
    includeBuildSummary: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    canvasSiteId: undefined,
    isUpdatingCanvasSiteId: false
  }),
  computed: {
    isCanvasSiteIdValid() {
      return this.isValidCanvasSiteId(this.canvasSiteId)
    }
  },
  created() {
    this.canvasSiteId = this.currentUser.canvasSiteId
    this.eventHub.on('current-user-update', () => {
      this.canvasSiteId = this.currentUser.canvasSiteId
    })
  },
  methods: {
    moment,
    updateCanvasSiteId() {
      if (this.currentUser.isAuthenticated && this.canvasSiteId.match(/^\d+$/)) {
        this.isUpdatingCanvasSiteId = true
        updateUserSession(this.canvasSiteId).then(data => {
          useContextStore().setCurrentUser(data)
          this.canvasSiteId = this.currentUser.canvasSiteId
          this.isUpdatingCanvasSiteId = false
          this.eventHub.emit('current-user-update')
        })
      }
    }
  }
}
</script>
