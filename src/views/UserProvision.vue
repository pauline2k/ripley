<template>
  <div v-if="!isLoading" class="page-user-provision">
    <Header1 id="page-title" class="page-user-provision-heading" text="Add Users to bCourses" />
    <form
      v-if="currentUser.isAdmin"
      id="user-import-form"
      name="userImportForm"
      @submit.prevent="onSubmit"
    >
      <v-row no-gutters>
        <label for="page-user-provision-uid-list" class="user-provision-uid-label mb-2 mt-3">
          Type or paste a list of U&ZeroWidthSpace;I&ZeroWidthSpace;D<span class="sr-only">'</span>s separated by spaces, commas, or line breaks
        </label>
        <textarea
          id="page-user-provision-uid-list"
          v-model="rawUids"
          :class="{'error': !isEmpty(validationErrors)}"
          rows="4"
          name="uids"
        >
        </textarea>
      </v-row>
      <v-row no-gutters>
        <v-col cols="8" class="pt-2">
          <div
            v-if="!status"
            id="user-provision-validation-msg"
            aria-live="polite"
            class="validation-messages"
            role="alert"
          >
            <div v-if="validationErrors.required">
              You must provide at least one
              <span aria-hidden="true">UID</span>
              <span class="sr-only">U I D</span>.
            </div>
            <div v-if="validationErrors.isNotNumeric">
              The following items in your list are not numeric: {{ invalidValues.join(', ') }}
            </div>
            <div v-if="validationErrors.isExceedingLimit">
              Maximum U&ZeroWidthSpace;I&ZeroWidthSpace;D<span class="sr-only">'</span>s: 200.
              {{ listLength }} U&ZeroWidthSpace;I&ZeroWidthSpace;D<span class="sr-only">'</span>s found in list.
            </div>
          </div>
          <div
            v-if="status"
            id="user-provision-status-msg"
            aria-live="polite"
            class="mx-3"
            role="alert"
          >
            <div v-if="status === 'error'">
              <v-icon icon="mdi-alert-circle-outline" class="icon-red mr-2" />
              <strong>Error: {{ error }}</strong>
            </div>
            <div v-if="status === 'success'" class="d-flex">
              <v-icon icon="mdi-check-circle" class="icon-green mr-2" />
              <div>
                <strong>
                  Success: the following <span v-if="size(importedUids) > 1">
                    {{ size(importedUids) }}
                  </span> U&ZeroWidthSpace;I&ZeroWidthSpace;D<span v-if="size(importedUids) > 1"><span class="sr-only">'</span>s
                  </span> <template v-if="size(importedUids) > 1">were</template><template v-else>was</template> imported into bCourses.
                </strong>
                <ul id="imported-uids-list" class="ml-3">
                  <li v-for="(uid, index) in importedUids" :key="index">{{ uid }}</li>
                </ul>
              </div>
            </div>
          </div>
        </v-col>
        <v-col cols="4">
          <div class="d-flex justify-end w-100">
            <v-btn
              id="user-provision-import-btn"
              aria-describedby="user-provisioning-progress"
              :aria-disabled="importButtonDisabled"
              class="text-no-wrap my-2"
              color="primary"
              :disabled="importButtonDisabled"
              type="submit"
            >
              <span v-if="!importProcessing">Import Users</span>
              <span v-if="importProcessing">
                <SpinnerWithinButton /> Importing Users...
              </span>
            </v-btn>
            <span id="user-provisioning-progress" class="sr-only" role="status">
              <span v-if="importProcessing">Importing Users</span>
            </span>
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
import Header1 from '@/components/utils/Header1.vue'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {each, isEmpty, size} from 'lodash'
import {importUsers} from '@/api/canvas-utility'

export default {
  name: 'UserProvision',
  components: {Header1, SpinnerWithinButton},
  mixins: [Context],
  data: () => ({
    error: undefined,
    importedUids: undefined,
    importProcessing: false,
    invalidValues: [],
    listLength: undefined,
    rawUids: '',
    status: undefined,
    validationErrors: {}
  }),
  computed: {
    importButtonDisabled() {
      return this.importProcessing || isEmpty(this.rawUids)
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
    handleError(errorMessage) {
      this.importProcessing = false
      this.status = 'error'
      this.error = errorMessage || 'Request to import users failed.'
    },
    isEmpty,
    onSubmit() {
      this.error = null
      this.importedUids = null
      this.status = null
      const validatedUids = this.validateUids()
      let importTimer
      if (validatedUids) {
        this.importProcessing = true
        importTimer = setInterval(() => {
          this.alertScreenReader('Still processing user import')
        }, 7000)
        importUsers(validatedUids).then(response => {
          clearInterval(importTimer)
          this.alertScreenReader('Imported users')
          this.importedUids = response.uids
          this.importProcessing = false
          this.rawUids = ''
          this.status = response.status
        }, this.handleError).catch(this.handleError)
      }
    },
    size,
    validateUids() {
      this.validationErrors = {}
      this.invalidValues = []
      const uids = this.rawUids.match(/\w+/g)
      if (!uids) {
        this.validationErrors.required = true
      }
      this.listLength = size(uids)
      if (this.listLength > 200) {
        this.validationErrors.isExceedingLimit = true
      }
      each(uids, uid => {
        if (isNaN(Number(uid))) {
          this.invalidValues.push(uid)
          this.validationErrors.isNotNumeric = true
        }
      })
      if (isEmpty(this.validationErrors)) {
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
    font-weight: 400;
  }
}
</style>
