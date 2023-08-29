<template>
  <div v-if="!isLoading" class="canvas-application page-user-provision">
    <h1 id="page-header" class="page-user-provision-heading">Add Users to bCourses</h1>
    <form
      v-if="currentUser.isAdmin"
      id="user-import-form"
      class="canvas-form pr-16"
      name="userImportForm"
      @submit.prevent="onSubmit"
    >
      <v-row no-gutters>
        <v-col cols="2">
          <label for="page-user-provision-uid-list" class="form-label user-provision-uid-label">
            <span aria-hidden="true">UID</span>
            <span class="sr-only">U I D</span>
            List
          </label>
        </v-col>
        <v-col cols="10">
          <textarea
            id="page-user-provision-uid-list"
            v-model="rawUids"
            :class="{'error': !$_.isEmpty(validationErrors)}"
            rows="4"
            name="uids"
            placeholder="Paste your list of UIDs here organized one UID per a line, or separated by spaces or commas."
          >
          </textarea>
          <div
            id="user-provision-validation-msg"
            aria-live="polite"
            class="validation-messages"
            role="alert"
          >
            <div v-if="validationErrors.required">
              You must provide at least one
              <span aria-hidden="true">UID</span>
              <span class="sr-only">U I D</span>
              .
            </div>
            <div v-if="validationErrors.isNotNumeric">
              The following items in your list are not numeric: {{ invalidValues.join(', ') }}
            </div>
            <div v-if="validationErrors.isExceedingLimit">
              Maximum IDs: 200. {{ listLength }} IDs found in list.
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="2"></v-col>
        <v-col cols="10">
          <div class="d-flex flex-wrap">
            <v-btn
              id="user-provision-import-btn"
              type="submit"
              class="canvas-button canvas-button-primary text-no-wrap mr-4 my-2"
              :disabled="importButtonDisabled"
            >
              <span v-if="!importProcessing">Import Users</span>
              <span v-if="importProcessing">
                <SpinnerWithinButton /> Processing Import...
              </span>
            </v-btn>
            <div
              id="user-provision-status-msg"
              role="alert"
              aria-live="polite"
              class="d-flex align-center"
            >
              <div v-if="status === 'error'">
                <v-icon icon="mdi-exclamation-circle" class="icon-red mr-2" />
                <strong>Error : {{ error }}</strong>
              </div>
              <div v-if="status === 'success'">
                <v-icon icon="mdi-check-circle" class="icon-green mr-2" />
                Success : The users specified were imported into bCourses.
              </div>
            </div>
          </div>
        </v-col>
      </v-row>
    </form>
    <v-alert
      v-if="!currentUser.isAdmin"
      class="ma-2"
      density="compact"
      role="alert"
      type="warning"
    >
      Unauthorized
    </v-alert>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {importUsers} from '@/api/canvas-utility'

export default {
  name: 'UserProvision',
  components: {SpinnerWithinButton},
  mixins: [Context],
  data: () => ({
    error: null,
    importProcessing: false,
    invalidValues: [],
    listLength: null,
    rawUids: '',
    status: null,
    validationErrors: {}
  }),
  computed: {
    importButtonDisabled() {
      return this.importProcessing || this.$_.isEmpty(this.rawUids)
    }
  },
  created() {
    this.$ready()
  },
  watch: {
    rawUids() {
      this.validationErrors = {}
    }
  },
  methods: {
    onSubmit() {
      this.error = null
      this.status = null
      const validatedUids = this.validateUids()
      if (validatedUids) {
        this.importProcessing = true
        importUsers(validatedUids).then(response => {
          this.importProcessing = false
          this.status = response.status
        }).catch(response => {
          this.importProcessing = false
          this.status = 'error'
          this.error = response.error
        })
      }
    },
    validateUids() {
      this.validationErrors = {}
      this.invalidValues = []
      const uids = this.rawUids.match(/\w+/g)
      if (!uids) {
        this.validationErrors.required = true
      }
      this.listLength = this.$_.size(uids)
      if (this.listLength > 200) {
        this.validationErrors.isExceedingLimit = true
      }
      this.$_.each(uids, uid => {
        if (isNaN(Number(uid))) {
          this.invalidValues.push(uid)
          this.validationErrors.isNotNumeric = true
        }
      })
      if (this.$_.isEmpty(this.validationErrors)) {
        return uids.join()
      }
    }
  }
}
</script>

<style scoped lang="scss">
.page-user-provision {
  color: $color-off-black;
  font-family: $body-font-family;
  font-size: 14px;
  font-weight: 300;
  padding: 10px 20px;
  .page-user-provision-heading {
    font-family: $body-font-family;
    font-size: 23px;
    font-weight: normal;
    margin: 10px 0;
  }
  .user-provision-uid-label {
    margin-top: 12px;
  }
}
</style>
