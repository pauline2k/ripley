<template>
  <div>
    <VueAnnouncer class="sr-only" />
    <div v-if="!isInIframe">
      <a
        id="skip-to-content-link"
        href="#content"
        class="sr-only sr-only-focusable"
        tabindex="0"
        @click="skipTo('#main-content')"
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
.background-splash {
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  min-height: 100vh;
}
.bc-header {
  color: $color-primary;
  font-family: 'Lato', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-weight: normal;
}
.bc-header1 {
  font-size: 24px;
  line-height: 30px;
  margin: 15px 0 16px;
}
.sr-only {
  position: absolute;
  left: -10000px;
  top: auto;
  width: 1px;
  height: 1px;
  overflow: hidden;
}
</style>
