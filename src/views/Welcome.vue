<template>
  <v-container
    v-if="!isLoading"
    class="background-splash h-100"
    fill-height
    fluid
    :style="{backgroundImage: `url(${muthur})`}"
  >
    <Header1 id="page-title" class="sr-only" text="Welcome" />
    <v-row align="center" class="mt-8" justify="center">
      <v-col>
        <v-card class="mx-auto" width="480">
          <div class="ma-5">
            <div>
              <h2 class="mb-0">Admin Tools</h2>
              <StandaloneToolsList :tools="adminTools" />
            </div>
            <div class="mt-1">
              <h2 class="mb-0">Embedded Tools</h2>
              <div v-if="!currentUser.canvasSiteId" class="ml-3 my-1">
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

            <div v-if="currentUser.isAdmin" class="mt-1">
              <h2 class="mb-0">Utilities</h2>
              <StandaloneToolsList :tools="utilities" />
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import muthur from '@/assets/images/muthur.png'
</script>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import StandaloneToolsList from '@/components/utils/StandaloneToolsList.vue'
import {
  mdiAccountMultiple,
  mdiAccountPlusOutline,
  mdiAccountSchool,
  mdiChartBarStacked,
  mdiCog,
  mdiEmailMultipleOutline,
  mdiExport,
  mdiWeb
} from '@mdi/js'
import {sortBy} from 'lodash'

export default {
  name: 'Welcome',
  mixins: [Context],
  components: {StandaloneToolsList, Header1},
  data: () => ({
    adminTools: [],
    embeddedTools: [],
    utilities: [
      {icon: mdiCog, title: 'Jobs', path: '/jobs'}
    ]
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
