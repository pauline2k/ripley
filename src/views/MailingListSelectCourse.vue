<template>
  <div class="canvas-application pa-5">
    <h1 id="page-header" tabindex="-1">Manage course site mailing list</h1>
    <v-alert
      v-if="error"
      id="manage-mailing-list-error"
      class="mb-2"
      density="compact"
      role="alert"
      type="warning"
    >
      {{ error }}
    </v-alert>
    <Alert :closable="true" :error-message="error" />
    <div class="align-center d-flex flex-wrap pa-3">
      <div class="pr-3">
        <label for="page-site-mailing-list-site-id" class="sr-only">Course Site ID</label>
        <v-text-field
          id="page-site-mailing-list-site-id"
          v-model="canvasSiteId"
          aria-required="true"
          :error="!!$_.trim(canvasSiteId) && !isCanvasSiteIdValid"
          hide-details
          maxlength="10"
          label="Canvas Course ID"
          required
          style="width: 200px"
          variant="outlined"
          @keydown.enter="submit"
        />
      </div>
      <div>
        <v-btn
          id="btn-get-mailing-list"
          color="primary"
          :disabled="isProcessing || !isCanvasSiteIdValid"
          @click="submit"
        >
          <span v-if="!isProcessing">Get Mailing List</span>
          <span v-if="isProcessing">
            <SpinnerWithinButton /> Searching...
          </span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Alert from '@/components/utils/Alert'
import Context from '@/mixins/Context'
import MailingList from '@/mixins/MailingList'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton'
import Utils from '@/mixins/Utils'
import {getMailingList} from '@/api/mailing-list'
import {getCanvasSite} from '@/api/canvas-course'

export default {
  name: 'MailingListSelectCourse',
  mixins: [Context, MailingList, Utils],
  components: {Alert, SpinnerWithinButton},
  data: () => ({
    error: undefined,
    isProcessing: false,
    canvasSiteId: undefined
  }),
  computed: {
    isCanvasSiteIdValid() {
      return this.isValidCanvasSiteId(this.canvasSiteId)
    }
  },
  mounted() {
    this.init()
    this.$putFocusNextTick('page-header')
    this.$ready()
  },
  methods: {
    submit() {
      if (!this.isProcessing && this.canvasSiteId) {
        this.isProcessing = true
        getMailingList(this.canvasSiteId).then(
          data => {
            this.error = undefined
            if (data) {
              this.setMailingList(data)
              this.$router.push({path: '/mailing_list/update'})
            } else {
              getCanvasSite(this.canvasSiteId).then(data => {
                this.setCanvasSite(data)
                this.$router.push({path: '/mailing_list/update'})
              })
            }
          },
          error => this.error = error
        ).then(() => this.isProcessing = false)
      }
    }
  }
}
</script>
