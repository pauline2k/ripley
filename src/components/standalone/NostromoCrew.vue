<template>
  <v-card
    v-if="nostromoCrew"
    class="elevation-2"
    color="grey-lighten-4"
    outlined
  >
    <v-card-title>
      <div class="align-start d-flex py-3">
        <h2 class="ml-2 mt-3">
          <div class="align-center d-flex">
            <div class="pr-2">
              <v-icon
                :color="$vuetify.theme.dark ? 'white' : 'primary'"
                :icon="mdiCardAccountDetails"
                size="large"
              />
            </div>
            <h2>The Nostromo Crew</h2>
          </div>
        </h2>
      </div>
    </v-card-title>
    <v-card-text>
      <v-data-table
        :headers="[
          {title: 'UID', key: 'uid', sortable: false},
          {title: 'Name', key: 'name', sortable: false},
          {title: 'Active', key: 'active', align: 'end', sortable: false},
          {title: 'Admin', key: 'isSuperuser', align: 'end', sortable: false},
          {title: 'Canvas Whitelist', key: 'isCanvasWhitelisted', align: 'end', sortable: false}
        ]"
        item-value="name"
        :items="nostromoCrew"
        density="compact"
        items-per-page="100"
      >
        <template #no-data>
          <div id="message-no-job-history" class="pa-4 text-no-wrap title">
            If we have no admin users then who is seeing this message?!
          </div>
        </template>
        <template #item.name="{item}">
          <div class="font-size-15 py-2 text-grey-darken-2">
            <span v-if="item.firstName || item.lastName">
              {{ item.lastName }}<span v-if="item.firstName && item.lastName">, </span>{{ item.firstName }}
            </span>
            <span v-if="!item.firstName && !item.lastName">
              &mdash;
            </span>
          </div>
        </template>
        <template #item.active="{item}">
          <v-icon
            :color="item.active ? 'success' : 'error'"
            :icon="item.active ? mdiCheckCircle : mdiAlert"
          />
        </template>
        <template #item.isSuperuser="{item}">
          <v-icon
            :color="item.isSuperuser ? 'success' : 'error'"
            :icon="item.isSuperuser ? mdiCheckCircle : mdiAlert"
          />
        </template>
        <template #item.isCanvasWhitelisted="{item}">
          <div class="float-right w-100">
            {{ item.isCanvasWhitelisted ? 'Yes' : 'No' }}
          </div>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import {mdiAlert, mdiCheckCircle, mdiCardAccountDetails} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {getNostromoCrew} from '@/api/user'
import {sortBy} from 'lodash'

export default {
  name: 'NostromoCrew',
  mixins: [Context],
  data: () => ({
    nostromoCrew: undefined
  }),
  created() {
    getNostromoCrew().then(data => {
      this.nostromoCrew = sortBy(data, ['lastName', 'firstName', 'uid'])
    })
  }
}
</script>
