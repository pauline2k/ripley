<template>
  <div v-if="!isLoading" class="pa-5">
    <Header1 text="Manage Mailing Lists" />
    <v-alert
      v-if="error"
      class="ma-2"
      density="compact"
      role="alert"
      type="warning"
    >
      {{ error }}
    </v-alert>
    <div v-if="currentUser.isAdmin" class="align-center d-flex flex-wrap pa-3">
      <div class="pr-3">
        <label for="page-site-mailing-list-site-id" class="sr-only">Course Site ID</label>
        <v-text-field
          id="page-site-mailing-list-site-id"
          v-model="canvasSiteId"
          aria-required="true"
          :error="!!trim(canvasSiteId) && !isCanvasSiteIdValid"
          hide-details
          maxlength="10"
          label="Canvas Course ID"
          required
          style="width: 200px"
          variant="outlined"
          @keydown.enter="proceed"
        />
      </div>
      <div>
        <v-btn
          id="btn-get-mailing-list"
          color="primary"
          :disabled="isProcessing || !isCanvasSiteIdValid"
          @click="proceed"
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
import Header1 from '@/components/utils/Header1.vue'
import MailingList from '@/mixins/MailingList'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton'
import {getMailingList} from '@/api/mailing-list'
import {isValidCanvasSiteId, putFocusNextTick} from '@/utils'
import {trim} from 'lodash'

export default {
  name: 'MailingListSelectCourse',
  components: {Header1, SpinnerWithinButton},
  mixins: [Context, MailingList],
  data: () => ({
    canvasSiteId: undefined,
    error: undefined,
    isProcessing: false
  }),
  computed: {
    isCanvasSiteIdValid() {
      return isValidCanvasSiteId(this.canvasSiteId)
    }
  },
  mounted() {
    if (this.currentUser.isAdmin) {
      this.init()
      putFocusNextTick('page-header')
    } else {
      this.error = 'Unauthorized'
    }
    this.$ready()
  },
  methods: {
    proceed() {
      if (!this.isProcessing) {
        this.isProcessing = true
        getMailingList(this.canvasSiteId).then(
          data => {
            this.error = undefined
            if (data) {
              this.setMailingList(data)
              this.$router.push('/mailing_list/update')
            } else {
              this.$router.push(`/mailing_list/create/${this.canvasSiteId}`)
            }
          },
          error => {
            this.error = error
            this.isProcessing = false
          }
        )
      }
    },
    trim
  }
}
</script>
