<template>
  <h2 id="course-site-details-header" class="mb-1 mt-3" tabindex="-1">Course Site Details</h2>
  <v-alert color="alert" border rounded>
    <div v-if="selectedSectionsList.length === 1">
      You are about to create a {{ currentSemesterName }} course site for
      {{ selectedSectionsList[0].courseTitle }} - {{ selectedSectionsList[0].courseCode }} ({{ selectedSectionsList[0].id }})
    </div>
    <div v-if="selectedSectionsList.length > 1">
      <div class="font-weight-medium">
        You are about to create a {{ currentSemesterName }} course site for:
      </div>
      <ul id="page-create-course-site-section-list" class="page-create-course-site-section-list">
        <li v-for="section in selectedSectionsList" :key="section.id">
          {{ section.courseTitle }} - {{ section.courseCode }} ({{ section.id }})
        </li>
      </ul>
    </div>
  </v-alert>
  <v-container fluid>
    <v-row align="center" class="mb-2" no-gutters>
      <v-col class="pr-2" cols="2">
        <label class="float-right font-weight-medium" for="course-site-name">
          Site Name
        </label>
      </v-col>
      <v-col cols="10">
        <v-text-field
          id="course-site-name"
          v-model="siteName"
          class="w-75"
          density="comfortable"
          :disabled="isCreating"
          :error="!trim(siteName)"
          hide-details
          maxlength="255"
          placeholder="Please provide site name"
          :required="true"
          variant="outlined"
          @keydown.enter="create"
        />
      </v-col>
    </v-row>
    <v-expand-transition>
      <v-row
        v-if="!trim(siteName)"
        align="center"
        class="mb-2"
        no-gutters
      >
        <v-col cols="2" />
        <v-col cols="10">
          <FormValidationAlert
            id="validation-error-in-site-name"
            class="w-75"
            text="Please provide site name."
          />
        </v-col>
      </v-row>
    </v-expand-transition>
    <v-row align="center" class="mt-2" no-gutters>
      <v-col class="pr-2" cols="2">
        <label class="float-right font-weight-medium" for="course-site-abbreviation">
          Site Abbreviation
        </label>
      </v-col>
      <v-col cols="10">
        <v-text-field
          id="course-site-abbreviation"
          v-model="siteAbbreviation"
          class="w-50"
          density="comfortable"
          :error="!trim(siteAbbreviation)"
          :disabled="isCreating"
          hide-details
          maxlength="42"
          placeholder="Please provide site abbreviation"
          :required="true"
          variant="outlined"
          @keydown.enter="create"
        />
      </v-col>
    </v-row>
    <v-expand-transition>
      <v-row
        v-if="!trim(siteAbbreviation)"
        align="center"
        class="mt-2"
        no-gutters
      >
        <v-col cols="2" />
        <v-col cols="10">
          <FormValidationAlert
            id="validation-error-in-site-abbreviation"
            class="w-50"
            text="Please provide site abbreviation."
          />
        </v-col>
      </v-row>
    </v-expand-transition>
    <v-row class="mt-2" no-gutters>
      <v-col cols="12">
        <div class="align-center d-flex float-right">
          <div class="mr-1">
            <v-btn
              id="create-course-site-button"
              color="primary"
              :disabled="isCreating || !trim(siteName) || !trim(siteAbbreviation)"
              @click="create"
            >
              <span v-if="isCreating">
                <v-progress-circular
                  class="mr-1"
                  indeterminate
                  size="18"
                />
                Creating...
              </span>
              <span v-if="!isCreating">
                Create Course Site
              </span>
            </v-btn>
          </div>
          <div>
            <v-btn
              id="go-back-button"
              :disabled="isCreating"
              variant="tonal"
              @click="goBack"
            >
              Cancel
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Context from '@/mixins/Context'
import FormValidationAlert from '@/components/utils/FormValidationAlert.vue'
import {iframeScrollToTop, putFocusNextTick} from '@/utils'
import {trim} from 'lodash'

export default {
  name: 'ConfirmationStep',
  components: {FormValidationAlert},
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
        this.courseSiteCreationPromise(this.siteName, this.siteAbbreviation).then(
          () => {
            this.isCreating = false
          },
          error => error
        ).finally(putFocusNextTick('page-title'))
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
