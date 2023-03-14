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
            v-model="canvasCourseId"
            :append-inner-icon="isUpdatingCanvasCourseId ? 'mdi-progress-check' : 'mdi-arrow-right-circle-outline'"
            density="compact"
            :disabled="isUpdatingCanvasCourseId"
            hide-details
            label="Canvas Course ID"
            maxlength="10"
            :error="!!$_.trim(canvasCourseId) && !isCanvasCourseIdValid"
            style="width: 200px"
            @click:append-inner="updateCanvasCourseId"
            @keydown.enter="updateCanvasCourseId"
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
    canvasCourseId: undefined,
    isUpdatingCanvasCourseId: false
  }),
  computed: {
    isCanvasCourseIdValid() {
      return this.isValidCanvasCourseId(this.canvasCourseId)
    }
  },
  created() {
    this.canvasCourseId = this.currentUser.canvasCourseId
    this.eventHub.on('current-user-update', () => {
      this.canvasCourseId = this.currentUser.canvasCourseId
    })
  },
  methods: {
    moment,
    updateCanvasCourseId() {
      if (this.currentUser.isAuthenticated && this.canvasCourseId.match(/^\d+$/)) {
        this.isUpdatingCanvasCourseId = true
        updateUserSession(this.canvasCourseId).then(data => {
          useContextStore().setCurrentUser(data)
          this.canvasCourseId = this.currentUser.canvasCourseId
          this.isUpdatingCanvasCourseId = false
          this.eventHub.emit('current-user-update')
        })
      }
    }
  }
}
</script>
