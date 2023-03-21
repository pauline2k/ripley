<template>
  <div class="canvas-application page-site-mailing-list">
    <h1 id="page-header" tabindex="-1">Manage course site mailing list</h1>
    <Alert
      :closable="true"
      :error-message="error"
      :success-message="success"
    />
    <div class="mt-4">
      <v-card id="mailing-list-details">
        <v-card-text>
          <h2 id="mailing-list-details-header" tabindex="-1">Mailing List</h2>
          <v-container>
            <v-row>
              <v-col>
                Name:
              </v-col>
              <v-col>
                <div>
                  <span class="ellipsis">{{ canvasSite.name }}</span>
                </div>
              </v-col>
            </v-row>
          </v-container>
          <div class="d-flex flex-wrap justify-space-between mb-2">
            <div id="mailing-list-canvas-code-and-term">{{ canvasSite.codeAndTerm }}</div>
            <div id="mailing-list-canvas-course-id">
              <span class="font-weight-medium">Site ID:</span>
              {{ canvasSite.canvasSiteId }}
            </div>
          </div>
        </v-card-text>
        <v-card-actions>
          <OutboundLink
            id="view-course-site-link"
            class="mb-3 px-3"
            :href="canvasSite.url"
          >
            View course site
          </OutboundLink>
        </v-card-actions>
      </v-card>
      <div class="py-8">
        <h2>Create Mailing List</h2>
        <div class="align-center d-flex flex-wrap pt-2">
          <div class="pr-3">
            <label for="mailing-list-name-input">Name:</label>
          </div>
          <div class="w-75">
            <v-text-field
              id="mailing-list-name-input"
              v-model="mailingListName"
              aria-required="true"
              hide-details
              maxlength="255"
              variant="outlined"
              required
              @keydown.enter="create"
            />
          </div>
        </div>
      </div>
      <div class="d-flex justify-end mt-4">
        <v-btn
          id="btn-cancel"
          class="mr-1"
          variant="text"
          @click="cancel"
        >
          Cancel
        </v-btn>
        <v-btn
          id="btn-create-mailing-list"
          color="primary"
          :disabled="isCreating"
          @click="create"
        >
          <span v-if="!isCreating">Create mailing list</span>
          <span v-if="isCreating">
            <SpinnerWithinButton /> Creating...
          </span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Alert from '@/components/utils/Alert'
import Context from '@/mixins/Context'
import MailingList from '@/mixins/MailingList.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import Utils from '@/mixins/Utils'
import {createMailingList} from '@/api/mailing-list'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'MailingListCreate',
  components: {Alert, OutboundLink, SpinnerWithinButton},
  mixins: [Context, MailingList, Utils],
  data: () => ({
    error: undefined,
    isCreating: false,
    mailingListName: undefined,
    success: undefined
  }),
  mounted() {
    if (this.canvasSite) {
      putFocusNextTick('page-header')
      this.$ready()
    } else {
      this.goToPath('/mailing_list/select_course')
    }
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled.')
    },
    create() {
      this.error = this.success = null
      const name = this.$_.trim(this.mailingListName)
      if (name) {
        this.isCreating = true
        this.$announcer.polite('Creating list')
        createMailingList(this.canvasSite.canvasSiteId, name).then(
          data => {
            this.setMailingList(data)
            putFocusNextTick('mailing-list-details-header')
          },
          error => this.error = error
        ).then(() => this.isCreating = false)
      }
    }
  }
}
</script>
