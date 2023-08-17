<template>
  <v-app>
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
    <v-main class="v-main-when-print">
      <PageLoadProgress v-if="isLoading" />
      <router-view v-if="applicationState.status === 200" />
      <Error v-if="applicationState.status !== 200" />
    </v-main>
  </v-app>
</template>

<script>
import Context from '@/mixins/Context'
import Error from '@/views/Error'
import PageLoadProgress from '@/components/utils/PageLoadProgress.vue'

export default {
  name: 'App',
  components: {Error, PageLoadProgress},
  mixins: [Context],
  methods: {
    skipTo: anchor => console.log(`TODO: VueScrollTo.scrollTo(${anchor}, 400)`)
  }
}
</script>

<style lang="scss">
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
.container {
  background: $color-container-grey-background !important;
  border: 1px solid $color-container-grey-border !important;
  border-radius: 3px !important;
  padding: 9px !important;
}

.icon-gold {
  color: $color-dark-tangerine;
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

h3.sections-course-title {
  display: inline !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  line-height: 20px;
}

select {
  appearance: auto !important;
  background: field !important;
  border: 1px solid $color-button-border !important;
  border-radius: 4px;
  color: $color-off-black;
  line-height: 20px !important;
  padding: 4px;
}
</style>
