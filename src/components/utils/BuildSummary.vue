<template>
  <span class="font-weight-bold text-body-1">
    Ripley v{{ $config.version }}
  </span>
  <span v-if="$_.get($config.build, 'gitCommit')" class="text-body-1">
    &mdash; Github: <a
      :href="`https://github.com/ets-berkeley-edu/ripley/commit/${$config.build.gitCommit}`"
      target="_blank"
    >
      {{ $config.build.gitCommit.substring(0, 7) }}<span class="sr-only"> (will open new browser tab)</span>
    </a>
  </span>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'BuildSummary',
  mixins: [Utils],
  data: () => ({
    summary: undefined
  })
}
</script>
