<template>
  <div>
    <div class="alert alert-info" role="alert">
      <h2 id="confirm-course-site-details-header" class="sr-only" tabindex="-1">Confirm Course Site Details</h2>
      <strong>
        You are about to create a {{ currentSemesterName }} course site with {{ pluralize('section', selectedSectionsList.length) }}:
      </strong>
      <ul id="page-create-course-site-section-list" class="page-create-course-site-section-list">
        <li v-for="section in selectedSectionsList" :key="section.sectionId">
          {{ section.courseTitle }} - {{ section.courseCode }} ({{ section.id }})
        </li>
      </ul>
    </div>
    <div>
      <form
        id="create-course-site-form"
        name="createCourseSiteForm"
        class="canvas-page-form"
        @submit.prevent="create"
      >
        <v-container fluid>
          <v-row>
            <v-col class="pr-1" md="3">
              <label for="siteName" class="form-label">
                Site Name:
              </label>
            </v-col>
            <v-col class="pl-0" md="6">
              <v-text-field
                id="siteName"
                v-model="siteName"
                class="w-100"
                name="siteName"
                :required="true"
              />
              <div v-if="!trim(siteName)" class="alert notice-error">
                <v-icon icon="mdi-exclamation-circle" class="left icon-red canvas-notice-icon" />
                Please fill out a site name.
              </div>
            </v-col>
          </v-row>
          <v-row>
            <v-col class="pr-1" md="3">
              <label for="siteAbbreviation" class="form-label">Site Abbreviation:</label>
            </v-col>
            <v-col class="pl-0" md="6">
              <v-text-field
                id="siteAbbreviation"
                v-model="siteAbbreviation"
                class="w-100"
                :required="true"
              />
              <div v-if="!trim(siteAbbreviation)" class="alert notice-error">
                <v-icon icon="mdi-exclamation-circle" class="left icon-red canvas-notice-icon" />
                Please fill out a site abbreviation.
              </div>
            </v-col>
          </v-row>
        </v-container>
        <div class="d-flex flex-row-reverse">
          <div>
            <v-btn
              id="create-course-site-button"
              aria-controls="page-create-course-site-steps-container"
              aria-label="Create Course Site"
              color="primary"
              :disabled="!trim(siteName) || !trim(siteAbbreviation)"
            >
              Create Course Site
            </v-btn>
          </div>
          <div class="pr-2">
            <v-btn
              id="go-back-button"
              @click="goBack"
            >
              Go Back
            </v-btn>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {iframeScrollToTop, pluralize, putFocusNextTick} from '@/utils'
import {trim} from 'lodash'

export default {
  name: 'ConfirmationStep',
  mixins: [Context],
  props: {
    currentSemesterName: {
      required: true,
      type: String
    },
    goBack: {
      required: true,
      type: Function
    },
    selectedSectionsList: {
      required: true,
      type: Array
    },
    startCourseSiteJob: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    siteAbbreviation: undefined,
    siteName: undefined
  }),
  created() {
    const section = this.selectedSectionsList[0]
    this.siteName = `${section.courseTitle} (${this.currentSemesterName})`
    this.siteAbbreviation = `${section.courseCode}-${section.instructionFormat}-${section.sectionNumber}`
    iframeScrollToTop()
    putFocusNextTick('confirm-course-site-details-header')
  },
  methods: {
    pluralize,
    create() {
      this.startCourseSiteJob(this.siteName, this.siteAbbreviation)
    },
    trim
  }
}
</script>

<style scoped lang="scss">
.page-create-course-site-section-list {
  list-style-type: disc;
  margin: 10px 0 0 39px;
}
</style>
