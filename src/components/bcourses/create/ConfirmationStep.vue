<template>
  <div>
    <h2 id="course-site-details-header" class="mb-2" tabindex="-1">Course Site Details</h2>
    <v-container class="ml-0 px-0" fluid max-width="100rem">
      <v-alert
        color="alert"
        border
        class="mb-4"
        role="none"
        rounded
      >
        <div v-if="selectedSectionsList.length === 1">
          You are about to create a {{ currentSemesterName }} course site for
          {{ selectedSectionsList[0].courseTitle }} - {{ selectedSectionsList[0].courseCode }} ({{ selectedSectionsList[0].id }})
        </div>
        <div v-if="selectedSectionsList.length > 1">
          <div class="font-weight-medium">
            You are about to create a {{ currentSemesterName }} course site for:
          </div>
          <ul id="page-create-course-site-section-list" class="list-bulleted page-create-course-site-section-list">
            <li v-for="section in selectedSectionsList" :key="section.id">
              {{ section.courseTitle }} - {{ section.courseCode }} ({{ section.id }})
            </li>
          </ul>
        </div>
      </v-alert>
      <v-row align="center" class="mb-2" no-gutters>
        <v-col md="4" lg="2">
          <label class="d-md-block text-right font-weight-medium" for="course-site-name">
            Site Name
          </label>
        </v-col>
        <v-col md="8" lg="10">
          <v-text-field
            id="course-site-name"
            v-model="siteName"
            autocomplete="on"
            class="ml-2r"
            density="comfortable"
            :disabled="isCreating"
            :error="!trim(siteName)"
            hide-details
            maxlength="255"
            :required="true"
            variant="outlined"
            @keydown.enter="create"
          />
        </v-col>
      </v-row>
      <v-expand-transition>
        <v-row
          v-show="!trim(siteName)"
          align="center"
          aria-live="polite"
          class="mb-2"
          no-gutters
        >
          <v-col lg="2" />
          <v-col lg="10">
            <FormValidationAlert
              id="validation-error-in-site-name"
              class="w-75"
              :show="!trim(siteName)"
              text="Please provide site name."
            />
          </v-col>
        </v-row>
      </v-expand-transition>
      <v-row align="center" class="mt-2" no-gutters>
        <v-col md="4" lg="2">
          <label class="d-md-block text-right font-weight-medium" for="course-site-abbreviation">
            Site Abbreviation
          </label>
        </v-col>
        <v-col md="8" lg="10">
          <v-text-field
            id="course-site-abbreviation"
            v-model="siteAbbreviation"
            autocomplete="on"
            class="ml-2r"
            density="comfortable"
            :error="!trim(siteAbbreviation)"
            :disabled="isCreating"
            hide-details
            maxlength="42"
            :required="true"
            variant="outlined"
            @keydown.enter="create"
          />
        </v-col>
      </v-row>
      <v-expand-transition>
        <v-row
          v-show="!trim(siteAbbreviation)"
          align="center"
          aria-live="polite"
          class="mt-2"
          no-gutters
        >
          <v-col md="4" lg="2" />
          <v-col md="8" lg="10">
            <FormValidationAlert
              id="validation-error-in-site-abbreviation"
              class="w-50"
              :show="!trim(siteAbbreviation)"
              text="Please provide site abbreviation."
            />
          </v-col>
        </v-row>
      </v-expand-transition>
      <v-row class="mt-2" no-gutters>
        <v-col cols="12">
          <div class="align-center d-flex flex-wrap justify-end">
            <v-btn
              id="create-course-site-button"
              class="mt-4 ml-3 w-100 w-sm-auto"
              color="primary"
              :disabled="isCreating || !trim(siteName) || !trim(siteAbbreviation)"
              @click="create"
            >
              <span v-if="isCreating">
                <SpinnerWithinButton />
                Creating...
              </span>
              <span v-if="!isCreating">
                Create Course Site
              </span>
            </v-btn>
            <v-btn
              id="go-back-button"
              class="mt-4 ml-3 w-100 w-sm-auto"
              :disabled="isCreating"
              variant="tonal"
              @click="goBack"
            >
              Cancel
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import FormValidationAlert from '@/components/utils/FormValidationAlert.vue'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {iframeScrollToTop, putFocusNextTick} from '@/utils'
import {trim} from 'lodash'

export default {
  name: 'ConfirmationStep',
  components: {FormValidationAlert, SpinnerWithinButton},
  mixins: [Context],
  props: {
    courseSiteCreationPromise: {
      required: true,
      type: Function
    },
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
    }
  },
  data: () => ({
    isCreating: false,
    siteAbbreviation: undefined,
    siteName: undefined
  }),
  created() {
    const section = this.selectedSectionsList[0]
    this.siteName = `${section.courseTitle} (${this.currentSemesterName})`
    this.siteAbbreviation = `${section.courseCode}-${section.instructionFormat}-${section.sectionNumber}`
    iframeScrollToTop()
    putFocusNextTick('course-site-details-header')
  },
  methods: {
    create() {
      if (!this.isCreating && trim(this.siteAbbreviation) && trim(this.siteName)) {
        this.isCreating = true
        const done = () => {
          this.isCreating = false
          putFocusNextTick('page-title')
        }
        this.courseSiteCreationPromise(this.siteName, this.siteAbbreviation).then(
          done,
          error => {
            done()
            return error
          }
        )
      }
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
