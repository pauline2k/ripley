<template>
  <div>
    <VueAnnouncer class="sr-only" />
    <div v-if="!$isInIframe">
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
import NotFound from '@/views/NotFound'

export default {
  name: 'App',
  components: {NotFound},
  mixins: [Context],
  methods: {
    skipTo: anchor => console.log(`TODO: VueScrollTo.scrollTo(${anchor}, 400)`)
  }
}
</script>

<style lang="scss">
* {
  text-transform: none !important;
}
.alert {
  background-color: $color-alert-background;
  border: 0;
  border-radius: 3px;
  color: $color-alert-foreground;
  font-size: 14px;
  font-weight: normal;
  margin: 10px 0;
  padding: 8px 15px 8px 14px;
  text-shadow: 0 1px 0 $color-white-translucent;
}
.alert-info {
  background-color: $color-alert-info-background;
  color: $color-alert-info-foreground;
}
.alert-success {
  background-color: $color-alert-success-background;
  color: $color-alert-success-foreground;
}
.alert-error {
  background-color: $color-alert-error-background;
  color: $color-alert-error-foreground;
}
.alert-container {
  margin: 10px 0;
}
.alert-error-icon {
  float: left;
  font-size: 38px;
  line-height: 45px;
  margin-right: 5px;
}
.alert-close-button-container {
  display: inline-block;
  float: right;

  .close-button {
    background-color: transparent;
    border: 0;
    margin: 0;
    padding: 0;
    &, &:hover, &:focus, &:active, &:visited {
      color: inherit;
      font-family: FontAwesome;
      font-size: 20px;
      text-decoration: none;
    }
  }
}
.background-splash {
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  min-height: 100vh;
}
.bg-white {
  background: $color-white;
}
.canvas-button {
  background: $color-button-background !important;
  border: 1px solid $color-button-border !important;
  box-shadow: none !important;
  font-family: $body-font-family;
  font-size: 14px !important;
  line-height: 20px;
  overflow: hidden;
  transition: background-color .2s ease-in-out 0s;
}
.canvas-button-primary,
.canvas-application .page-roster .roster-search .button-blue {
  background: $color-button-primary-background !important;
  color: $color-button-primary-color !important;
  &:hover, &:active, &:focus {
    background: $color-button-primary-hover-background !important;
    border-color: $color-button-primary-border !important;
    box-shadow: none !important;
    color: $color-button-primary-color !important;
  }
  &[disabled] {
    color: $color-button-primary-color !important;
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
    font-family: $body-font-family;
    font-size: 14px;
    line-height: 20px;
    margin-bottom: 10px;
    padding: 8px;
    &[disabled] {
      color: $color-grey;
    }
  }
}
.canvas-notice-icon {
  font-size: 20px;
  line-height: 20px;
  margin-right: 5px;
}
.canvas-page-form {
  background: transparent;
  border: 0;
  padding: 0;
}
.ellipsis {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.font-size-16 {
  font-size: 16px;
}
.icon-gold {
  color: $color-dark-tangerine;
}
.notice-text-container {
  line-height: 18px;
  margin-left: 52px;
}
.notice-text-header {
  color: $color-off-black;
  font-size: 16px;
  font-weight: 500;
  line-height: 20px;
  margin: 4px 0;
}
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
h1 {
  color: $color-off-black;
  font-family: $body-font-family;
  font-size: 24px;
  font-weight: 500;
  line-height: 30px;
  margin: 15px 0 16px;
}
h2 {
  color: $color-off-black;
  font-family: $body-font-family;
  font-size: 20px;
  font-weight: normal;
}
h3 {
  color: $color-off-black;
  font-family: $body-font-family;
  font-size: 18px;
  font-weight: normal;
}
.sections-course-container {
  background: $color-container-grey-background !important;
  border: 1px solid $color-container-grey-border !important;
  border-radius: 3px !important;
  padding: 9px !important;
}
h3.sections-course-title {
  display: inline !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  line-height: 20px;
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
