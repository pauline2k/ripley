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
        density="compact"
        :headers="[
          {title: 'UID', key: 'uid', sortable: false},
          {title: 'Name', key: 'name', sortable: false}
        ]"
        item-value="name"
        :items="nostromoCrew"
        hide-default-footer
        disable-pagination
        :items-per-page="0"
      >
        <template #no-data>
          <div id="message-no-job-history" class="pa-4 text-no-wrap title">
            If we have no admin users then who is seeing this message?!
          </div>
        </template>
        <template #item.uid="{item}">
          <div class="py-2">
            {{ item.uid }}
          </div>
        </template>
        <template #item.name="{item}">
          <div class="font-size-15 py-2 text-grey-darken-2">
            <img class="profile-image" :src="item.image" :alt="item.firstName">
            <span v-if="item.firstName || item.lastName" class="profile-name">
              <OutboundLink :href="`https://www.berkeley.edu/directory/?search-term=${item.firstName}+${item.lastName}`">
                <span>
                  {{ item.firstName || '' }} {{ item.lastName || '' }}
                </span>
              </OutboundLink>
            </span>
            <span v-if="!item.firstName && !item.lastName">
              &mdash;
            </span>
          </div>
        </template>
        <template #bottom></template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import {mdiCardAccountDetails} from '@mdi/js'
</script>


<script>
import Context from '@/mixins/Context'
import {getNostromoCrew} from '@/api/user'
import OutboundLink from '@/components/utils/OutboundLink'

import {sortBy} from 'lodash'

export default {
  name: 'NostromoCrew',
  mixins: [Context],
  data: () => ({
    nostromoCrew: undefined
  }),
  created() {
    getNostromoCrew().then(data => {
      this.nostromoCrew = sortBy(data, ['firstName', 'lastName', 'uid'])
      const images = [
        'Alien_Harry_Dean_Stanton1.webp',
        'Alien_Ian_Holm1.webp',
        'Alien_John_Hurt2.webp',
        'Alien_Sigourney1.webp',
        'Alien_Tom_Skerritt1.webp',
        'Alien_Veronica_Cartwright1.webp',
        'Alien_Yaphet_Kotto1.webp']
      this.nostromoCrew.forEach(item => {
        item.image = `src/assets/images/${images[this.randomNumberGenerator(0, images.length - 1)]}`
      })
    })
  },
  methods: {
    randomNumberGenerator(min, max) {
      min = Math.ceil(min)
      max = Math.floor(max)
      return Math.floor(Math.random() * (max - min + 1)) + min
    }
  }
}
</script>

<style scoped lang="scss">
  .profile-image {
    height: 40px;
    width: auto;
    border-radius: 50%;
  }

  .profile-name {
    position: relative;
    bottom: 13px;
    left: 16px;
  }

</style>
