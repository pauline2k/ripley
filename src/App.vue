<template>
  <div>
    <VueAnnouncer class="sr-only" />
    <div v-if="!isInIframe">
      <a
        id="skip-to-content-link"
        href="#content"
        class="sr-only sr-only-focusable"
        tabindex="0"
        @click="skipTo('#cc-main-content')"
      >
        Skip to content
      </a>
    </div>
    <router-view v-if="applicationState.status === 200" />
    <NotFound v-if="applicationState.status !== 200" />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import IFrameMixin from '@/mixins/IFrameMixin'
import NotFound from '@/views/NotFound'

export default {
  name: 'App',
  components: {NotFound},
  mixins: [Context, IFrameMixin],
  methods: {
    skipTo: anchor => '' // TODO: VueScrollTo.scrollTo(anchor, 400)
  }
}
</script>

<style lang="scss">
  @use './settings';
</style>

<style>
@import './assets/styles/ripley-global.css';
</style>
