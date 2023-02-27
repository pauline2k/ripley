<template>
  <div class="align-center d-flex">
    <div class="pr-2">
      <a class="text-decoration-none" href="/" title="Link to home">
        <v-icon color="primary" icon="mdi-alien" size="large" />
      </a>
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
import Utils from '@/mixins/Utils'

export default {
  name: 'BuildSummary',
  mixins: [Context, Utils],
  data: () => ({
    summary: undefined
  })
}
</script>
