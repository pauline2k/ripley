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
          <v-icon
            :color="theme.global.current.value.dark ? 'white' : 'primary'"
            :icon="mdiCardAccountDetails"
            size="large"
          />
          The Nostromo Crew
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
            <img
              :alt="item.firstName"
              class="profile-image"
              :src="item.image"
            >
            <span v-if="item.firstName || item.lastName" class="profile-name">
              <OutboundLink :href="`https://www.berkeley.edu/directory/?search-term=${item.firstName}+${item.lastName}`">
                {{ item.firstName || '' }} {{ item.lastName || '' }}
              </OutboundLink>
            </span>
            <span v-if="!item.firstName && !item.lastName">
              &mdash;
            </span>
          </div>
        </template>
        <template #bottom />
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import {each, sortBy} from 'lodash'
import {mdiCardAccountDetails} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useTheme} from 'vuetify'
import {getNostromoCrew} from '@/api/user'
import HarryDeanStanton from '@/assets/images/harry_dean_stanton.webp'
import IanHolm from '@/assets/images/alien_ian_holm.webp'
import JohnHurt from '@/assets/images/alien_john_hurt.webp'
import OutboundLink from '@/components/utils/OutboundLink'
import Sigourney from '@/assets/images/alien_sigourney.webp'
import TomSkerritt from '@/assets/images/alien_tom_skerritt.webp'
import VeronicaCartwright from '@/assets/images/alien_veronica_cartwright.webp'
import YaphetKotto from '@/assets/images/alien_yaphet_kotto.webp'

const nostromoCrew = ref()
const theme = useTheme()

onMounted(() => {
  getNostromoCrew().then(data => {
    nostromoCrew.value = sortBy(data, ['firstName', 'lastName', 'uid'])
    const images = [
      HarryDeanStanton,
      IanHolm,
      JohnHurt,
      Sigourney,
      TomSkerritt,
      VeronicaCartwright,
      YaphetKotto
    ]
    each(nostromoCrew.value, (member, index) => {
      member.image = images[index % images.length]
    })
  })
})
</script>

<style scoped lang="scss">
.profile-image {
  background-size: cover;
  border-radius: 5px;
  height: 40px;
  object-fit: cover;
  width: 40px;
}
.profile-name {
  position: relative;
  bottom: 13px;
  left: 16px;
}
</style>
