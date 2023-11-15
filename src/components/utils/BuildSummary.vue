<template>
  <div class="align-center d-flex">
    <div class="pr-2">
      <span v-if="!offerHomeLink">
        <v-icon color="primary" :icon="mdiAlien" size="large" />
      </span>
      <router-link
        v-if="offerHomeLink"
        id="link-to-home"
        class="text-decoration-none"
        to="/"
      >
        <span class="sr-only">Home</span>
        <v-icon color="primary" :icon="mdiAlien" size="large" />
      </router-link>
    </div>
    <div>
      <span class="font-weight-bold text-body-1">
        Ripley v{{ config.version }}
      </span>
      <span v-if="get(config, 'build.gitCommit')" class="text-body-1">
        &mdash; Github: <a
          :href="`https://github.com/ets-berkeley-edu/ripley/commit/${config.build.gitCommit}`"
          target="_blank"
        >
          {{ config.build.gitCommit.substring(0, 7) }}<span class="sr-only"> (will open new browser tab)</span>
        </a>
      </span>
    </div>
  </div>
</template>

<script setup>
import {get} from 'lodash'
import {mdiAlien} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const context = useContextStore()
const config = context.config
const currentUser = context.currentUser
const isHome = get(useRoute().meta, 'isHome')
const offerHomeLink = currentUser.canAccessStandaloneView && (!isHome || context.applicationState.status !== 200)
</script>
