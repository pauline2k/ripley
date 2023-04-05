<template>
  <div v-if="!isLoading" class="canvas-application mx-10 my-5">
    <h1 id="page-header" class="mt-0" tabindex="-1">Create Mailing List</h1>
    <v-alert
      v-if="success"
      class="ma-2"
      :closable="true"
      density="compact"
      role="alert"
      type="success"
    >
      {{ success }}
    </v-alert>
    <v-alert
      v-if="error"
      class="ma-2"
      :closable="true"
      density="compact"
      role="alert"
      type="warning"
    >
      {{ error }}
    </v-alert>
    <div class="mt-4">
      <v-card id="mailing-list-details" elevation="3">
        <v-card-title>
          <div class="pl-1 pt-2">
            <h2>Canvas Course Site</h2>
          </div>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  Name:
                </div>
              </v-col>
              <v-col>
                <OutboundLink
                  id="mailing-list-course-site-name"
                  class="pr-2"
                  :href="canvasSite.url"
                >
                  {{ canvasSite.name }}
                </OutboundLink>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  ID:
                </div>
              </v-col>
              <v-col>
                {{ canvasSite.canvasSiteId }}
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="2">
                <div class="float-right font-weight-medium pr-3">
                  Description:
                </div>
              </v-col>
              <v-col>
                {{ canvasSite.codeAndTerm }}
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
      <div class="mt-8">
        <h2>Create Mailing List</h2>
        <v-container fluid>
          <v-row no-gutters align="start">
            <v-col cols="1">
              <div class="float-right pr-3 pt-4">
                <label for="mailing-list-name-input" class="font-weight-medium">Name:</label>
              </div>
            </v-col>
            <v-col cols="7">
              <div v-if="currentUser.isTeaching && !currentUser.isAdmin">
                {{ mailingListName }}
              </div>
              <v-text-field
                v-if="currentUser.isAdmin"
                id="mailing-list-name-input"
                v-model="mailingListName"
                aria-required="true"
                hide-details
                maxlength="255"
                variant="outlined"
                required
                @keydown.enter="create"
              />
              <div class="has-invalid-characters">
                <div v-if="hasInvalidCharacters" class="d-flex text-red">
                  <div class="pr-1 text-no-wrap">Name may contain neither spaces nor: </div>
                  <div><pre>{{ $_.join([...$_.trim(invalidCharacters)], ' ') }}</pre></div>
                </div>
              </div>
            </v-col>
            <v-col>
              <div class="d-flex pt-3">
                <div>
                  <v-btn
                    id="btn-cancel"
                    class="mx-1"
                    variant="text"
                    @click="cancel"
                  >
                    Cancel
                  </v-btn>
                </div>
                <div>
                  <v-btn
                    id="btn-create-mailing-list"
                    color="primary"
                    :disabled="isCreating || !$_.trim(mailingListName) || hasInvalidCharacters"
                    @click="create"
                  >
                    <span v-if="!isCreating">Create mailing list</span>
                    <span v-if="isCreating">
                      <SpinnerWithinButton /> Creating...
                    </span>
                  </v-btn>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import MailingList from '@/mixins/MailingList.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {createMailingList, getSuggestedMailingListName} from '@/api/mailing-list'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'MailingListCreate',
  components: {OutboundLink, SpinnerWithinButton},
  mixins: [Context, MailingList],
  data: () => ({
    error: undefined,
    invalidCharacters: ' "(),:;<>@[\\]',
    isCreating: false,
    mailingListName: undefined,
    success: undefined
  }),
  computed: {
    hasInvalidCharacters() {
      const name = this.$_.trim(this.mailingListName)
      return this.$_.intersection([...name], [...this.invalidCharacters]).length
    }
  },
  mounted() {
    if (this.currentUser.isTeaching || this.currentUser.isAdmin) {
      if (this.canvasSite) {
        getSuggestedMailingListName(this.canvasSite.canvasSiteId).then(data => {
          this.mailingListName = data
          putFocusNextTick('page-header')
          this.$ready()
        })
      } else {
        this.$router.push({path: '/mailing_list/select_course'})
      }
    } else {
      this.$router.push({path: '/404'})
    }
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled.')
      this.$router.push({path: '/mailing_list/select_course'})
    },
    create() {
      this.error = this.success = null
      const name = this.$_.trim(this.mailingListName)
      if (name && !this.hasInvalidCharacters) {
        this.isCreating = true
        this.$announcer.polite('Creating list')
        createMailingList(this.canvasSite.canvasSiteId, name).then(
          data => {
            this.setMailingList(data)
            this.$router.push('/mailing_list/update')
          },
          error => this.error = error
        ).then(() => this.isCreating = false)
      }
    }
  }
}
</script>

<style scoped lang="scss">
.has-invalid-characters {
  min-height: 24px;
}
</style>
