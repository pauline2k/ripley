<template>
  <div class="canvas-application page-create-project-site">
    <div v-if="!isLoading && !error">
      <h1 class="page-create-project-site-header">Create a Project Site</h1>
      <form class="bg-transparent border-0 canvas-form" @submit.prevent="createProjectSite">
        <v-container>
          <v-row>
            <v-col class="float-right" sm="3">
              <label for="page-create-project-site-name" class="page-create-project-site-form-label">Project Site Name</label>
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
          <button
            id="create-project-site-button"
            :disabled="isCreating || !$_.trim(name)"
            aria-controls="page-reader-alert"
            class="canvas-button canvas-button-primary"
            type="submit"
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
          </button>
          <v-btn
            id="cancel-and-return-to-site-creation"
            type="button"
            aria-label="Cancel and return to Site Creation Overview"
            class="canvas-button"
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
import IFrameMixin from '@/mixins/IFrameMixin'
import {createProjectSite} from '@/api/course'

export default {
  name: 'CreateProjectSite',
  mixins: [Context, IFrameMixin],
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
      const path = this.isInIframe ? '/lti/create_site' : '/create_site'
      this.$router.push({path})
    },
    createProjectSite() {
      this.isCreating = true
      this.$announcer.polite('Creating new project site...')
      createProjectSite(this.name).then(data => {
        if (data.projectSiteUrl) {
          if (this.isInIframe) {
            this.iframeParentLocation(data.projectSiteUrl)
          } else {
            window.location.href = data.projectSiteUrl
          }
        } else {
          this.error = 'Failed to create project site.'
          this.isCreating = false
        }
      })
    }
  }
}
</script>

<style scoped lang="scss">
.page-create-project-site {
  background: $color-white;
  padding: 20px;

  .page-create-project-site-form-label {
    font-size: 16px;
    font-weight: bold;
    text-align: right;
  }

  .page-create-project-site-header {
    font-size: 24px;
    line-height: 30px;
    margin: 15px 0 16px;
  }

  @media #{$small-only} {
    .page-create-project-site-form-label {
      text-align: left;
    }
  }
}
</style>
