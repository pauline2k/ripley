<template>
  <div>
    <h2 class="visuallyhidden">Course Site Creation</h2>
    <div aria-live="polite">
      <div v-show="!jobStatus" class="page-create-course-site-pending-request">
        <v-progress-circular
          class="mr-2"
          color="primary"
          indeterminate
        />
        Sending request...
      </div>
      <div v-if="jobStatus === 'New'" class="page-create-course-site-pending-request">
        <v-progress-circular
          class="mr-2"
          color="primary"
          indeterminate
        />
        Course provisioning request sent. Awaiting processing....
      </div>
      <div v-if="jobStatus && jobStatus !== 'Completed'">
        <div id="page-create-course-site-progress-bar-outer">
          <ProgressBar :percent-complete-rounded="Math.round(percentComplete * 100)" />
        </div>
        <div v-if="jobStatus === 'Error'">
          <BackgroundJobError :error-config="errorConfig" :errors="errors" />
          <div class="page-create-course-site-step-options">
            <div>
              <div class="form-actions">
                <button
                  id="start-over-button"
                  type="button"
                  aria-controls="page-create-course-site-selecting-step"
                  aria-label="Start over course site creation process"
                  @click="fetchFeed"
                >
                  Start Over
                </button>
                <button
                  id="go-back-button"
                  type="button"
                  aria-controls="page-create-course-site-confirmation-step"
                  aria-label="Go Back to Site Details Confirmation"
                  @click="showConfirmation"
                >
                  Back
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="jobStatus === 'Completed'" :aria-expanded="`${jobStatus === 'Completed'}`">
      <v-progress-circular
        class="mr-2"
        color="primary"
        indeterminate
      />
      <div class="visuallyhidden" role="alert">
        Redirecting to new course site.
      </div>
    </div>
  </div>
</template>

<script>
import BackgroundJobError from '@/components/bcourses/shared/BackgroundJobError'
import ProgressBar from '@/components/bcourses/shared/ProgressBar'

export default {
  name: 'MonitoringJob',
  components: {
    BackgroundJobError,
    ProgressBar
  },
  props: {
    fetchFeed: {
      required: true,
      type: Function
    },
    jobStatus: {
      default: undefined,
      required: false,
      type: String
    },
    percentComplete: {
      required: true,
      type: Number
    },
    showConfirmation: {
      required: true,
      type: Function
    }
  }
}
</script>

<style scoped lang="scss">
.page-create-course-site-pending-request {
  margin: 15px auto;
}

.page-create-course-site-step-options {
  padding: 20px 0;
}
</style>
