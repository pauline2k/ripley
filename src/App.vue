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
form {
  .validation-messages {
    color: $color-harley-davidson-orange;
    font-size: 14px;
    font-weight: 500;
    min-height: 20px;
    margin: 0 12px 4px;
  }
  input[type="number"],
  input[type="password"],
  input[type="text"],
  textarea {
    -moz-appearance: none;
    -webkit-appearance: none;
    background: $color-white;
    border: 1px solid $color-very-light-grey;
    border-radius: 3px !important;
    box-shadow: inset 0 1px 2px $color-whisper;
    font-size: 14px;
    font-weight: normal;
    margin: 0 0 4px;
    padding: 8px 12px;
    width: 100%;
    &[disabled] {
      color: $color-grey;
    }
    &.error{
      border: 1px solid $color-harley-davidson-orange !important;
      color: $color-harley-davidson-orange !important;
      font-weight: 500;
    }
  }
  .form-label {
    display: block;
    font-size: 13px;
    font-weight: 400;
    margin-right: 10px;
    margin-top: 8px;
    text-align: right;
  }
  select {
    -moz-appearance: none;
    -webkit-appearance: none;
    background: $color-white;
    border: 1px solid $color-very-light-grey;
    border-radius: 0;
    font-family: $body-font-family;
    font-size: 14px;
    font-weight: 500;
    height: 38px;
    margin: 0 0 4px;
    padding: 8px 14px 8px 9px;
    width: 100%;
    &[disabled] {
      color: $color-grey;
    }
  }
  textarea {
    resize: vertical;
  }
  ::placeholder {
    color: $color-nobel;
  }
}
.container {
  background: $color-container-grey-background !important;
  border: 1px solid $color-container-grey-border !important;
  border-radius: 3px !important;
  padding: 9px !important;
}
.icon-blue {
  color: $color-help-link-blue;
}
.icon-gold {
  color: $color-dark-tangerine;
}
.icon-green {
  color: $color-salem;
}
.icon-red {
  color: $color-harley-davidson-orange;
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
body, .v-application {
  color: $color-body-black !important;
  font-family: $body-font-family !important;
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
table {
  border: 1px solid $color-container-grey-border;
  border-collapse: separate;
  border-radius: 3px;
  border-spacing: 0;
  margin: 0;
  width: 100%;
  tbody tr td {
    border-top: solid 1px $color-container-grey-border;
    color: $color-body-black;
    font-size: 14px;
    font-weight: 400;
    padding-left: 14px;
    vertical-align: top;
  }
  thead tr th {
    background-color: transparent;
    color: $color-body-black;
    font-size: 13px;
    font-weight: 500;
    padding: 6px 10px 6px 14px;
    text-align: start;
  }
  td {
    border-bottom-color: $color-table-cell-border-grey;
  }
  &.table-striped {
    tbody {
      tr:nth-child(odd) {
        background-color: $color-table-cell-bg-grey;
      }
      tr:nth-of-type(even) {
        background-color: $color-white;
      }
    }
  }
}
</style>
