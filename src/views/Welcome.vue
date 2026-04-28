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
import {
  mdiAccountMultiple,
  mdiAccountPlusOutline,
  mdiAccountSchool,
  mdiChartBarStacked,
  mdiEmailMultipleOutline,
  mdiExport,
  mdiWeb
} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {sortBy} from 'lodash'
import Header1 from '@/components/utils/Header1.vue'
import muthur from '@/assets/images/muthur.png'
import ToolPortfolio from '@/components/standalone/ToolPortfolio.vue'
import {useContextStore} from '@/stores/context'

const adminTools = ref([])
const contextStore = useContextStore()
const embeddedTools = ref([])

onMounted(() => {
  loadTools()
  contextStore.eventHub.on('current-user-update', () => {
    loadTools()
  })
  contextStore.loadingComplete()
})

const loadTools = () => {
  const canvasSiteId = contextStore.currentUser.canvasSiteId
  adminTools.value = sortBy([
    {disabled: false, icon: mdiWeb, path: '/manage_sites', title: 'Manage Sites'},
    {disabled: false, icon: mdiAccountPlusOutline, path: '/provision_user', title: 'User Provision'},
    {disabled: false, icon: mdiEmailMultipleOutline, path: '/mailing_list/select_course', title: 'Mailing Lists Manager'},
  ], tool => tool.title)
  embeddedTools.value = sortBy([
    {disabled: !canvasSiteId, icon: mdiEmailMultipleOutline, path: '/mailing_list/create', title: 'Mailing List'},
    {disabled: !canvasSiteId, icon: mdiExport, path: '/export_grade', title: 'E-Grade Export'},
    {disabled: !canvasSiteId, icon: mdiChartBarStacked, path: '/grade_distribution', title: 'Grade Distribution'},
    {disabled: !canvasSiteId, icon: mdiAccountSchool, path: '/add_user', title: 'Find a Person to Add'},
    {disabled: !canvasSiteId, icon: mdiAccountMultiple, path: '/roster', title: 'Roster Photos'}
  ], tool => tool.title)
}
</script>
