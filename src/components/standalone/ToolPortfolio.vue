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
      <div v-if="config.devAuthEnabled" class="mt-3">
        <h2 class="mb-0">Canvas Site Tools</h2>
        <div v-if="!currentUser.canvasSiteId" class="mt-3">
          <v-alert
            density="compact"
            role="alert"
            type="info"
          >
            If you enter a Canvas site ID (see top of page) then the following links will become available.
          </v-alert>
        </div>
        <StandaloneToolsList :tools="embeddedTools" />
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import {mdiStackOverflow} from '@mdi/js'
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
import {sortBy} from 'lodash'
import StandaloneToolsList from '@/components/utils/StandaloneToolsList.vue'

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
    embeddedTools: []
  }),
  created() {
    this.loadTools()
    this.eventHub.on('current-user-update', () => {
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
    }
  }
}
</script>
