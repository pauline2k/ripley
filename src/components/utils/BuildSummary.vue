<template>
  <div class="align-center d-flex">
    <div class="pr-2">
      <span v-if="$route.meta.isHome">
        <v-icon color="primary" icon="mdi-alien" size="large" />
      </span>
      <router-link
        v-if="!$route.meta.isHome"
        id="link-to-home"
        class="text-decoration-none"
        to="/"
      >
        <span class="sr-only">Home</span>
        <v-icon color="primary" icon="mdi-alien" size="large" />
      </router-link>
    </div>
    <div>
      <span class="font-weight-bold text-body-1">
        Ripley v{{ config.version }}
      </span>
      <span v-if="$_.get(config, 'build.gitCommit')" class="text-body-1">
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

<script>
import Context from '@/mixins/Context'

export default {
  name: 'BuildSummary',
  mixins: [Context],
  data: () => ({
    summary: undefined
  })
}
</script>
