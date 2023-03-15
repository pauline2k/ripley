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
    <div class="align-center d-flex flex-wrap pa-3">
      <div class="pr-3">
        <label for="page-site-mailing-list-site-id" class="sr-only">Course Site ID</label>
        <v-text-field
          id="page-site-mailing-list-site-id"
          v-model="canvasCourseId"
          aria-required="true"
          :error="!!$_.trim(canvasCourseId) && !isCanvasCourseIdValid"
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
          :disabled="isProcessing || !isCanvasCourseIdValid"
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
import Context from '@/mixins/Context'
import MailingList from '@/mixins/MailingList'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import Utils from '@/mixins/Utils'
import {getMailingList} from '@/api/mailing-list'
import {getCanvasSite} from '@/api/course'

export default {
  name: 'MailingListSelectCourse',
  components: {SpinnerWithinButton},
  mixins: [Context, MailingList, Utils],
  data: () => ({
    error: undefined,
    isProcessing: false,
    canvasCourseId: undefined
  }),
  computed: {
    isCanvasCourseIdValid() {
      return this.isValidCanvasCourseId(this.canvasCourseId)
    }
  },
  mounted() {
    this.init()
    this.$putFocusNextTick('page-header')
    this.$ready()
  },
  methods: {
    submit() {
      if (!this.isProcessing && this.canvasCourseId) {
        this.isProcessing = true
        getMailingList(this.canvasCourseId).then(
          data => {
            this.error = undefined
            if (data) {
              this.setMailingList(data)
              this.$router.push({path: '/mailing_list/update'})
            } else {
              getCanvasSite(this.canvasCourseId).then(data => {
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
