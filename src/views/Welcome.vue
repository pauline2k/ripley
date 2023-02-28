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
        <v-card class="mx-auto" width="320">
          <div class="ma-5">
            <h2 class="mb-0">Tools</h2>
            <v-list density="compact" :lines="false">
              <v-list-item v-for="(tool, index) in tools" :key="index">
                <template #prepend>
                  <v-icon class="mr-4" :icon="tool.icon" />
                </template>
                <v-list-item-title>
                  <router-link class="text-decoration-none" :to="tool.path">
                    {{ tool.title }}
                  </router-link>
                </v-list-item-title>
              </v-list-item>
            </v-list>
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
    tools: [
      {icon: 'mdi-google-classroom', title: 'Create a Course Site', path: '/create_course_site'},
      {icon: 'mdi-projector-screen-outline', title: 'Create a Project Site', path: '/create_project_site'},
      {icon: 'mdi-export', title: 'E-Grade Export', path: '/grade_export/:id'},
      {icon: 'mdi-account-school', title: 'Find a User to Add', path: '/add_user/:id'},
      {icon: 'mdi-email-fast-outline', title: 'Mailing List', path: '/mailing_list/:id'},
      {icon: 'mdi-email-multiple-outline', title: 'Mailing Lists', path: '/mailing_lists'},
      {icon: 'mdi-google-classroom', title: 'Official Sections', path: '/manage_official_sections/:id'},
      {icon: 'mdi-account-multiple', title: 'Roster Photos', path: '/rosters/:id'},
      {icon: 'mdi-web', title: 'Site Creation', path: '/create_site'},
      {icon: 'mdi-account-plus-outline', title: 'User Provision', path: '/provision_user'}
    ],
    utilities: [
      {icon: 'mdi-cog', title: 'Jobs', path: '/jobs'}
    ]
  })
}
</script>
