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
            <div v-if="!currentUser.canvasCourseId">
              Certain tools are unavailable because the current user has a null <span class="font-italic">canvas_course_id</span>.
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
                  active-color="primary"
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
    this.$eventHub.on('current-user-update', () => {
      this.loadTools()
    })
  },
  methods: {
    loadTools() {
      const canvasCourseId = this.currentUser.canvasCourseId
      this.tools = this.$_.sortBy([
        {disabled: false, icon: 'mdi-google-classroom', path: '/create_course_site', title: 'Create a Course Site'},
        {disabled: false, icon: 'mdi-projector-screen-outline', path: '/create_project_site', title: 'Create a Project Site'},
        {disabled: false, icon: 'mdi-email-multiple-outline', path: '/mailing_lists', title: 'Mailing Lists'},
        {disabled: false, icon: 'mdi-web', path: '/create_site', title: 'Site Creation'},
        {disabled: false, icon: 'mdi-account-plus-outline', path: '/provision_user', title: 'User Provision'},
        {disabled: !canvasCourseId, icon: 'mdi-export', path: `/grade_export/${canvasCourseId}`, title: 'E-Grade Export'},
        {disabled: !canvasCourseId, icon: 'mdi-account-school', path: `/add_user/${canvasCourseId}`, title: 'Find a User to Add'},
        {disabled: !canvasCourseId, icon: 'mdi-email-fast-outline', path: `/mailing_list/${canvasCourseId}`, title: 'Mailing List'},
        {disabled: !canvasCourseId, icon: 'mdi-google-classroom', path: `/manage_official_sections/${canvasCourseId}`, title: 'Official Sections'},
        {disabled: !canvasCourseId, icon: 'mdi-account-multiple', path: `/rosters/${canvasCourseId}`, title: 'Roster Photos'}
      ], tool => tool.title)
    }
  }
}
</script>
