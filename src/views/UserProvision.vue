<template>
  <div v-if="!isLoading" class="canvas-application page-user-provision">
    <v-container fluid>
      <v-row no-gutters>
        <h1 class="page-user-provision-heading">Add Users to bCourses</h1>
      </v-row>
      <form name="userImportForm" @submit="onSubmit">
        <v-row no-gutters>
          <v-col cols="10">
            <v-container fluid>
              <v-row no-gutters>
                <v-col cols="2">
                  <label for="page-user-provision-uid-list" class="form-label">
                    <span aria-hidden="true">UID</span>
                    <span class="sr-only">U I D</span>
                    List
                  </label>
                </v-col>
                <v-col cols="10">
                  <textarea
                    id="page-user-provision-uid-list"
                    v-model="rawUids"
                    class="page-user-provision-uid-list-input"
                    rows="4"
                    name="uids"
                    placeholder="Paste your list of UIDs here organized one UID per a line, or separated by spaces or commas."
                  >
                  </textarea>
                  <small v-if="validationErrors.required" role="alert" aria-live="polite">
                    You must provide at least one
                    <span aria-hidden="true">UID</span>
                    <span class="sr-only">U I D</span>
                    .
                  </small>
                  <small v-if="validationErrors.isNotNumeric" role="alert" aria-live="polite">
                    The following items in your list are not numeric: {{ invalidValues.join(', ') }}
                  </small>
                  <small v-if="validationErrors.isExceedingLimit" role="alert" aria-live="polite">
                    Maximum IDs: 200. {{ listLength }} IDs found in list.
                  </small>
                </v-col>
              </v-row>
              <v-row no-gutters>
                <v-col cols="2"></v-col>
                <v-col cols="2">
                  <button
                    type="submit"
                    class="canvas-button canvas-button-primary d-block"
                    :disabled="importButtonDisabled"
                  >
                    Import Users
                  </button>
                </v-col>
                <v-col cols="8">
                  <div role="alert" aria-live="polite">
                    <div v-if="importProcessing">
                      <span class="sr-only">Processing import</span>
                      <v-progress-circular
                        color="primary"
                        indeterminate
                      />
                    </div>
                    <div v-if="status === 'error'" class="page-user-provision-feedback">
                      <v-icon icon="mdi-exclamation-circle" class="icon-red mr-2" />
                      <strong>Error : {{ error }}</strong>
                    </div>
                    <div v-if="status === 'success'" class="page-user-provision-feedback">
                      <v-icon icon="mdi-check-circle" class="icon-green mr-2" />
                      Success : The users specified were imported into bCourses.
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-col>
        </v-row>
      </form>
    </v-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {importUsers} from '@/api/canvas-utility'

export default {
  name: 'UserProvision',
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
      return this.importProcessing || !this.rawUids.length
    }
  },
  created() {
    this.$ready()
  },
  methods: {
    onSubmit(evt) {
      evt.preventDefault()
      this.error = null
      const validatedUids = this.validateUids()
      if (validatedUids) {
        this.importProcessing = true
        this.status = null
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
      this.listLength = uids.length
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

  .page-user-provision-uid-list-input {
    padding: 8px 12px;
  }

  .page-user-provision-feedback {
    padding: 5px 0 15px;
    div {
      margin-top: 5px;
    }
  }

  small {
    font-weight: 300;
  }
}
</style>
