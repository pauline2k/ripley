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
        <ToolPortfolio :v-card-class="`mx-auto`" :width="480" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import Header1 from '@/components/utils/Header1.vue'
import muthur from '@/assets/images/muthur.png'
import ToolPortfolio from '@/components/standalone/ToolPortfolio.vue'
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

export default {
  name: 'Welcome',
  mixins: [Context],
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
