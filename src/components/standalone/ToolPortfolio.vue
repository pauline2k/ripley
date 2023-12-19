<template>
  <v-card class="pb-2 px-8" :class="vCardClass" :width="width">
    <v-card-title>
      <div
        class="align-end d-flex mt-6"
        :class="{'mb-2': config.devAuthEnabled}"
      >
        <div class="mb-1 mr-2">
          <v-icon
            color="primary"
            :icon="mdiStackOverflow"
            size="large"
          />
        </div>
        <div>
          <h2>{{ config.devAuthEnabled ? 'LTI Portfolio' : 'Tools' }}</h2>
        </div>
      </div>
    </v-card-title>
    <v-card-text :class="{'ml-2': !config.devAuthEnabled}">
      <h2 v-if="config.devAuthEnabled" class="mb-0">Account Tools</h2>
      <StandaloneToolsList :tools="adminTools" />
      <div v-if="config.devAuthEnabled && currentUser.canAccessStandaloneView" class="mt-3">
        <h2 class="mb-0">Canvas Site Tools</h2>
        <v-alert
          v-if="!currentUser.canvasSiteId"
          class="mt-2"
          density="compact"
          role="alert"
          type="info"
        >
          Enter a Canvas site ID (below) to enable site tools.
        </v-alert>
        <div v-if="currentUser.canvasSiteId" class="align-center d-flex pt-2">
          <a
            :href="`${config.canvasApiUrl}/courses/${canvasSiteId}`"
            class="text-subtitle-1"
            target="_blank"
            title="Open course site in new tab"
          >
            <span class="canvas-site-name">{{ currentUser.canvasSiteName }}</span><v-icon class="ml-1" :icon="mdiOpenInNew" size="small" />
          </a>
        </div>
        <StandaloneToolsList :tools="embeddedTools" />
        <div class="align-center d-flex pt-1">
          <div class="pr-2">
            <v-text-field
              id="update-canvas-course-id"
              v-model="canvasSiteId"
              density="compact"
              :disabled="isUpdatingCanvasSiteId || isLoading"
              :error="!!trim(canvasSiteId) && !isCanvasSiteIdValid"
              hide-details
              maxlength="10"
              style="width: 124px"
              variant="outlined"
              @keydown.enter="updateCanvasSiteId"
            />
          </div>
          <div>
            <v-btn
              id="update-canvas-site-id-btn"
              color="primary"
              :disabled="isUpdatingCanvasSiteId"
              @click="updateCanvasSiteId"
            >
              <span v-if="isUpdatingCanvasSiteId">
                <SpinnerWithinButton /> Changing...
              </span>
              <span v-if="!isUpdatingCanvasSiteId">Change Canvas Site ID</span>
            </v-btn>
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton'
import {mdiOpenInNew, mdiStackOverflow} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {
  mdiAccountMultiple,
  mdiAccountPlusOutline,
  mdiAccountSchool,
  mdiChartBarStacked,
  mdiEmailMultipleOutline,
  mdiExport,
  mdiWeb
} from '@mdi/js'
import StandaloneToolsList from '@/components/utils/StandaloneToolsList.vue'
import {isNil, sortBy, trim} from 'lodash'
import {updateUserSession} from '@/api/auth'
import {useContextStore} from '@/stores/context'
import {isValidCanvasSiteId} from '@/utils'

export default {
  name: 'ToolPortfolio',
  components: {StandaloneToolsList},
  mixins: [Context],
  props: {
    vCardClass: {
      default: undefined,
      required: false,
      type: String
    },
    width: {
      default: undefined,
      required: false,
      type: Number
    }
  },
  data: () => ({
    adminTools: [],
    canvasSiteId: undefined,
    embeddedTools: [],
    error: undefined,
    expansionPanel: false,
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
    this.loadTools()
    this.eventHub.on('current-user-update', () => {
      this.canvasSiteId = this.currentUser.canvasSiteId
      this.loadTools()
    })
    this.$ready()
  },
  methods: {
    loadTools() {
      const canvasSiteId = this.currentUser.canvasSiteId
      this.adminTools = sortBy([
        {disabled: false, icon: mdiWeb, path: '/manage_sites', title: 'Manage Sites'},
        {disabled: false, icon: mdiAccountPlusOutline, path: '/provision_user', title: 'User Provision'},
        {disabled: false, icon: mdiEmailMultipleOutline, path: '/mailing_list/select_course', title: 'Mailing Lists Manager'},
      ], tool => tool.title)
      this.embeddedTools = sortBy([
        {disabled: !canvasSiteId, icon: mdiEmailMultipleOutline, path: '/mailing_list/create', title: 'Mailing List'},
        {disabled: !canvasSiteId, icon: mdiExport, path: '/export_grade', title: 'E-Grade Export'},
        {disabled: !canvasSiteId, icon: mdiChartBarStacked, path: '/grade_distribution', title: 'Grade Distribution'},
        {disabled: !canvasSiteId, icon: mdiAccountSchool, path: '/add_user', title: 'Find a Person to Add'},
        {disabled: !canvasSiteId, icon: mdiAccountMultiple, path: '/roster', title: 'Roster Photos'}
      ], tool => tool.title)
    },
    updateCanvasSiteId() {
      const canvasSiteId = trim(this.canvasSiteId) || null
      const isValid = isNil(canvasSiteId) || Number.isInteger(canvasSiteId) || canvasSiteId.match(/^\d+$/)
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

<style scoped>
.canvas-site-name {
  font-weight: 410;
}
</style>
