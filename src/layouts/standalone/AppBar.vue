<template>
  <v-app-bar class="display-none-when-print" flat>
    <v-app-bar-title>
      <div class="align-center d-flex flex-wrap justify-space-between">
        <div class="me-auto">
          <BuildSummary />
        </div>
        <div v-if="currentUser.isAuthenticated" class="align-center d-flex pr-5">
          <div v-if="canvasSiteId" class="pr-2">
            <a
              :href="`${config.canvasApiUrl}/courses/${canvasSiteId}`"
              target="_blank"
              title="Open course site in new tab"
            >
              <v-img
                alt="Logo of Canvas, by Instructure"
                aspect-ratio="1"
                src="@/assets/images/canvas-by-instructure.png"
                width="30"
              />
            </a>
          </div>
          <div class="my-2">
            <v-text-field
              id="update-canvas-course-id"
              v-model="canvasSiteId"
              :append-inner-icon="isUpdatingCanvasSiteId ? 'mdi-progress-check' : 'mdi-arrow-right-circle-outline'"
              density="compact"
              :disabled="isUpdatingCanvasSiteId || isLoading"
              :error="!!$_.trim(canvasSiteId) && !isCanvasSiteIdValid"
              hide-details
              label="Canvas Site ID"
              maxlength="10"
              style="width: 200px"
              variant="outlined"
              @click:append-inner="updateCanvasSiteId"
              @keydown.enter="updateCanvasSiteId"
            />
          </div>
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
  <v-snackbar
    v-model="showError"
    :close-delay="4000"
    location="top"
    variant="elevated"
  >
    {{ error }}
  </v-snackbar>
</template>

<script>
import AppBarMenu from '@/components/utils/AppBarMenu.vue'
import BuildSummary from '@/components/utils/BuildSummary'
import Context from '@/mixins/Context'
import moment from 'moment'
import {updateUserSession} from '@/api/auth'
import {useContextStore} from '@/stores/context'
import {isValidCanvasSiteId} from '@/utils'

export default {
  name: 'AppBar',
  mixins: [Context],
  components: {AppBarMenu, BuildSummary},
  props: {
    includeBuildSummary: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    canvasSiteId: undefined,
    error: undefined,
    isUpdatingCanvasSiteId: false
  }),
  computed: {
    isCanvasSiteIdValid() {
      return isValidCanvasSiteId(this.canvasSiteId)
    },
    showError: {
      get() {
        return !!this.error
      },
      set(flag) {
        this.error = flag ? this.error : undefined
      }
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
      const canvasSiteId = this.$_.trim(this.canvasSiteId) || null
      const isValid = this.$_.isNil(canvasSiteId) || Number.isInteger(canvasSiteId) || canvasSiteId.match(/^\d+$/)
      if (isValid && this.currentUser.isAuthenticated) {
        this.isUpdatingCanvasSiteId = true
        updateUserSession(canvasSiteId).then(
          data => {
            useContextStore().setCurrentUser(data)
            this.canvasSiteId = this.currentUser.canvasSiteId
            this.isUpdatingCanvasSiteId = false
            this.$router.go()
          },
          error => {
            this.error = error
            this.$router.push({path: '/'})
          }
        )
      }
    }
  }
}
</script>
