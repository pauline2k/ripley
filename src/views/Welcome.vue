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
            <h2 class="mb-0">Tools</h2>
            <div v-if="!currentUser.canvasSiteId">
              Certain tools are unavailable because the current user has a null <span class="font-italic">canvas_site_id</span>.
            </div>
            <div v-if="!currentUser.isAdmin">
              The current user is not an Admin. Expect authorization errors.
            </div>
            <v-list density="compact" :lines="false">
              <template v-for="(tool, index) in tools" :key="index">
                <v-list-item v-if="!tool.disabled">
                  <template #prepend>
                    <v-icon class="mr-4" :icon="tool.icon" />
                  </template>
                  <v-list-item-title>
                    <router-link
                      v-if="!tool.disabled"
                      class="text-decoration-none"
                      :to="tool.path"
                    >
                      {{ tool.title }}
                    </router-link>
                  </v-list-item-title>
                </v-list-item>
              </template>
            </v-list>
            <div v-if="currentUser.isAdmin">
              <h2 class="mb-0 mt-5">Utilities</h2>
              <v-list density="compact" :items="utilities" :lines="false">
                <v-list-item
                  v-for="(utility, index) in utilities"
                  :key="index"
                  color="primary"
                >
                  <template #prepend>
                    <v-icon class="mr-4" :icon="utility.icon" />
                  </template>
                  <v-list-item-title>
                    <router-link class="text-decoration-none" :to="utility.path">
                      {{ utility.title }}
                    </router-link>
                  </v-list-item-title>
                </v-list-item>
              </v-list>
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

export default {
  name: 'Welcome',
  mixins: [Context],
  data: () => ({
    tools: [],
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
      const isAdmin = this.currentUser.isAdmin
      this.tools = this.$_.sortBy([
        {disabled: false, icon: 'mdi-web', path: '/create_site', title: 'Create a Site'},
        {disabled: false, icon: 'mdi-account-plus-outline', path: '/provision_user', title: 'User Provision'},
        {disabled: !isAdmin, icon: 'mdi-email-multiple-outline', path: '/mailing_list/select_course', title: 'Mailing Lists Manager'},
        {disabled: !canvasSiteId, icon: 'mdi-email-multiple-outline', path: '/mailing_list/create', title: `Mailing List of Canvas Site ${canvasSiteId}`},
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
