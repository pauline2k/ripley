<template>
  <div class="mx-10 my-5">
    <h1>Create a Project Site</h1>
    <div v-if="!isLoading">
      <CanvasErrors v-if="error" :message="error" />
      <div class="align-center d-flex justify-center pb-8 pt-4">
        <div class="pr-3">
          <label for="page-create-project-site-name" class="font-weight-medium text-subtitle-1">Project Site Name</label>
        </div>
        <div class="w-50">
          <v-text-field
            id="page-create-project-site-name"
            v-model="name"
            class="w-100"
            density="comfortable"
            :disabled="isCreating"
            hide-details
            maxlength="50"
            required
            placeholder="Enter a name for your site"
            variant="outlined"
            @keydown.enter="createProjectSite"
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
          :disabled="isCreating || !trim(name)"
        >
          <span v-if="!isCreating">Create a Project Site</span>
          <span v-if="isCreating">
            <v-progress-circular
              class="mr-2"
              color="primary"
              indeterminate
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
    createProjectSite() {
      this.isCreating = true
      this.$announcer.polite('Creating new project site...')
      createProjectSite(this.name).then(data => {
        if (data.projectSiteUrl) {
          if (this.$isInIframe) {
            iframeParentLocation(data.projectSiteUrl)
          } else {
            window.location.href = data.projectSiteUrl
          }
        } else {
          this.error = 'Failed to create project site.'
          this.isCreating = false
        }
      })
    },
    trim
  }
}
</script>
