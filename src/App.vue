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
a {
  color: $primary-color;
  text-decoration: none;
  &:hover {
    cursor: pointer;
  }
  &:hover, &:focus {
    text-decoration: underline;
  }
}
.background-splash {
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  min-height: 100vh;
}
.canvas-button-primary,
.canvas-application .page-roster .roster-search .button-blue {
  background: $color-button-primary-background;
  border: 1px solid $color-button-primary-border;
  color: $color-button-primary-color;
  &:hover, &:active, &:focus {
    background: $color-button-primary-hover-background;
    border-color: $color-button-primary-border;
    box-shadow: none;
    color: $color-button-primary-color;
  }
  &[disabled] {
    color: $color-button-primary-color;
  }
}
.canvas-form {
  label {
    padding: 9px 0;
  }
  input[type="text"] {
    border: 1px solid $color-grey;
    border-radius: 3px;
    color: $color-off-black;
    display: inline-block;
    font-family: 'Lato', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 20px;
    margin-bottom: 10px;
    padding: 8px;
    &[disabled] {
      color: $color-grey;
    }
  }
}
.canvas-page-form {
  background: transparent;
  border: 0;
  padding: 0;
}
.form-actions {
  display: flex;
  justify-content: right;
  margin: 5px 0;
}
.header {
  color: $color-primary;
  font-family: 'Lato', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-weight: normal;
}
.header1 {
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
