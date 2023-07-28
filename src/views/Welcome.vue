<template>
  <v-container
    v-if="!isLoading"
    class="background-splash h-100"
    fill-height
    fluid
    :style="{backgroundImage: `url(${muthur})`}"
  >
    <v-row align="center" class="mt-8" justify="center">
      <v-col>
        <v-card class="mx-auto" width="480">
          <div class="ma-5">
            <div>
              <h2 class="mb-0">Admin Tools</h2>
              <StandaloneToolsList class="pt-0" :tools="adminTools" />
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
              <StandaloneToolsList class="pt-0" :tools="embeddedTools" />
            </div>

            <div v-if="currentUser.isAdmin" class="mt-1">
              <h2 class="mb-0">Utilities</h2>
              <StandaloneToolsList class="pt-0" :tools="utilities" />
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
import StandaloneToolsList from '@/components/utils/StandaloneToolsList.vue'

export default {
  name: 'Welcome',
  mixins: [Context],
  components: {StandaloneToolsList},
  data: () => ({
    adminTools: [],
    embeddedTools: [],
    utilities: [
      {icon: 'mdi-cog', title: 'Jobs', path: '/jobs'}
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
      this.adminTools = this.$_.sortBy([
        {disabled: false, icon: 'mdi-web', path: '/create_site', title: 'Create a Site'},
        {disabled: false, icon: 'mdi-account-plus-outline', path: '/provision_user', title: 'User Provision'},
        {disabled: false, icon: 'mdi-email-multiple-outline', path: '/mailing_list/select_course', title: 'Mailing Lists Manager'},
      ], tool => tool.title)
      this.embeddedTools = this.$_.sortBy([
        {disabled: !canvasSiteId, icon: 'mdi-email-multiple-outline', path: '/mailing_list/create', title: 'Mailing List'},
        {disabled: !canvasSiteId, icon: 'mdi-export', path: '/grade_export', title: 'E-Grade Export'},
        {disabled: !canvasSiteId, icon: 'mdi-chart-bar-stacked', path: '/grade_distribution', title: 'Grade Distribution'},
        {disabled: !canvasSiteId, icon: 'mdi-account-school', path: '/add_user', title: 'Find a User to Add'},
        {disabled: !canvasSiteId, icon: 'mdi-google-classroom', path: '/manage_official_sections', title: 'Official Sections'},
        {disabled: !canvasSiteId, icon: 'mdi-account-multiple', path: '/roster', title: 'Roster Photos'}
      ], tool => tool.title)
    }
  }
}
</script>
