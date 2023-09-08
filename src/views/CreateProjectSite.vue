<template>
  <div class="canvas-application">
    <div v-if="!isLoading && !error">
      <h1>Create a Project Site</h1>
      <form class="bg-transparent border-0 canvas-form" @submit.prevent="createProjectSite">
        <v-container>
          <v-row>
            <v-col class="float-right" sm="3">
              <label for="page-create-project-site-name">Project Site Name</label>
            </v-col>
            <v-col class="pl-0 pt-2" sm="9">
              <v-text-field
                id="page-create-project-site-name"
                v-model="name"
                class="w-50"
                :disabled="isCreating"
                placeholder="Enter a name for your site"
              />
            </v-col>
          </v-row>
        </v-container>
        <div class="d-flex justify-end mt-4">
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
          <v-btn
            id="cancel-and-return-to-site-creation"
            type="button"
            aria-label="Cancel and return to Site Creation Overview"
            variant="link"
            @click="cancel"
          >
            Cancel
          </v-btn>
        </div>
      </form>
    </div>
    <div v-if="error" class="alert-container">
      <CanvasErrors :message="error" />
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
      const path = this.$isInIframe ? '/lti/create_site' : '/create_site'
      this.$router.push({path})
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
