<template>
  <div>
    <VueAnnouncer class="sr-only" />
    <div v-if="!isInIframe" class="cc-accessibility-links">
      <a
        id="skip-to-content-link"
        href="#cc-main-content"
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

<style scoped lang="scss">
.cc-accessibility-links {
  position: relative;
  z-index: 1;

  a {
    background: $cc-color-white;
    display: block;
    font-weight: bold;
    padding: 8px;
    position: absolute;
    top: -999em;
    z-index: 1;
    &:focus, &:active {
      left: 50%;
      margin-left: -100px;
      text-align: center;
      top: 5px;
      width: 200px;
    }
  }
}
</style>

<style lang="scss">
@import 'styles/colors';

.background-splash {
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  min-height: 100vh;
}
</style>

<style scoped lang="scss">
.cc-accessibility-links {
  position: relative;
  z-index: 1;

  a {
    background: $cc-color-white;
    display: block;
    font-weight: bold;
    padding: 8px;
    position: absolute;
    top: -999em;
    z-index: 1;
    &:focus, &:active {
      left: 50%;
      margin-left: -100px;
      text-align: center;
      top: 5px;
      width: 200px;
    }
  }
}
</style>
