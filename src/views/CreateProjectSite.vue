<template>
  <div class="mx-10 my-5">
    <h1>Create a Project Site</h1>
    <div v-if="!isLoading">
      <CanvasErrors v-if="error" :message="error" />
      <div class="align-center d-flex justify-center pb-8 pt-4">
        <div class="pr-3">
          <label for="page-create-project-site-name" class="font-weight-medium text-subtitle-1">Project Site Name</label>
        </div>
        <div class="mr-16 w-50">
          <v-text-field
            id="page-create-project-site-name"
            v-model="name"
            class="w-100"
            density="comfortable"
            :disabled="isCreating"
            hide-details
            maxlength="255"
            placeholder="Enter a name for your site"
            required
            variant="outlined"
            @keydown.enter="create"
          />
        </div>
      </div>
      <div class="pb-8 pr-2">
        <v-divider />
      </div>
      <div class="d-flex justify-end">
        <v-btn
          id="cancel-and-return-to-site-creation"
          aria-label="Cancel and return to Site Creation Overview"
          class="mx-1"
          :disabled="isCreating"
          type="button"
          variant="text"
          @click="cancel"
        >
          Cancel
        </v-btn>
        <v-btn
          id="create-project-site-button"
          aria-controls="page-reader-alert"
          class="mr-2"
          color="primary"
          type="submit"
          :disabled="isCreating || !trim(name)"
          @click="create"
        >
          <span v-if="!isCreating">Create a Project Site</span>
          <span v-if="isCreating">
            <v-progress-circular
              class="mr-1"
              indeterminate
              size="18"
            />
            Creating...
          </span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import CanvasErrors from '@/components/bcourses/CanvasErrors'
import Context from '@/mixins/Context'
import {createProjectSite} from '@/api/canvas-site'
import {iframeParentLocation} from '@/utils'
import {trim} from 'lodash'

export default {
  name: 'CreateProjectSite',
  mixins: [Context],
  components: {CanvasErrors},
  data: () => ({
    isCreating: undefined,
    error: undefined,
    name: undefined
  }),
  created() {
    this.$ready('Create bCourses Project Site', 'page-create-project-site-name')
  },
  methods: {
    cancel() {
      this.$router.push({path: '/create_site'})
    },
    create() {
      if (!this.isCreating && trim(name)) {
        this.error = null
        this.isCreating = true
        this.$announcer.polite('Creating new project site...')
        createProjectSite(this.name).then(
          data => {
            if (this.$isInIframe) {
              iframeParentLocation(data.url)
            } else {
              window.location.href = data.url
            }
          },
          error => {
            this.error = error
          }
        ).finally(() => {
          this.isCreating = false
        })
      }
    },
    trim
  }
}
</script>
