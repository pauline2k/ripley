<template>
  <div v-if="!contextStore.isLoading" class="px-3">
    <Header1 class="mb-2" text="Update Mailing List" />
    <v-alert
      v-if="!hasUpdatedSincePageLoad && !noChangesAlert && !isUpdating"
      id="mailing-list-created-alert"
      class="my-2"
      density="compact"
      role="none"
      type="info"
    >
      The list "{{ mailingList.name }}@{{ mailingList.domain }}" has been created.
      To add members, click the "Update Memberships" button below.
    </v-alert>
    <v-alert
      v-if="noChangesAlert"
      id="mailing-list-no-changes-alert"
      class="my-2"
      density="compact"
      role="none"
      :text="noChangesAlert"
      type="info"
    />
    <v-expansion-panels
      v-if="alerts.length"
      id="mailing-list-update-alert"
      v-model="openPanelIndex"
      :aria-label="alertsLabel"
      class="mb-4"
      color="info"
      role="list"
    >
      <v-expansion-panel
        v-for="(alert, index) in alerts"
        :key="index"
        :readonly="!size(alert.emailAddresses)"
        role="listitem"
      >
        <v-expansion-panel-title
          :id="`mailing-list-alert-${index}`"
          :aria-controls="`mailing-list-alert-panel-${index}`"
          :color="alert.type"
        >
          <span>
            {{ alert.message }}
            <span aria-hidden="true">[&ThinSpace;</span>
            <span class="toggle-show-hide">{{ openPanelIndex === index ? 'hide' : 'show' }}</span><span class="sr-only"> details</span>
            <span aria-hidden="true">&ThinSpace;]</span>
          </span>
          <template #actions>
            <v-icon color="white" :icon="alert.type === 'errors' ? mdiAlertCircle : mdiCheck" />
          </template>
        </v-expansion-panel-title>
        <v-expansion-panel-text :id="`mailing-list-alert-panel-${index}`">
          <ul id="mailing-list-members" class="mt-2">
            <li
              v-for="emailAddress in alert.emailAddresses"
              :key="emailAddress"
              class="text-truncate px-md-4 py-1 mb-1"
            >
              <v-icon
                class="d-none d-sm-inline-block mr-2 mr-md-6"
                :color="alert.type === 'errors' ? 'red' : 'primary'"
                :icon="mdiAccount"
              />
              {{ emailAddress }}
            </li>
          </ul>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
    <div>
      <v-card id="mailing-list-details" class="pl-md-3" elevation="2">
        <v-card-text class="px-4">
          <h2 id="course-site-header">bCourses Site</h2>
          <v-container
            aria-labelledby="course-site-header"
            class="py-3"
            fluid
            tag="dl"
          >
            <v-row no-gutters>
              <v-col
                class="font-weight-medium"
                cols="12"
                md="3"
                tag="dt"
              >
                Name
              </v-col>
              <v-col
                class="pl-4"
                cols="12"
                md="9"
                tag="dd"
              >
                <OutboundLink
                  id="mailing-list-course-site-name"
                  aria-describedby="course-site-header"
                  class="font-size-15 font-weight-medium"
                  :href="canvasSite.url"
                >
                  {{ canvasSite.name }}
                </OutboundLink>
              </v-col>
            </v-row>
            <v-row class="mt-2r" no-gutters>
              <v-col
                class="font-weight-medium"
                cols="12"
                md="3"
                tag="dt"
              >
                Canvas Site ID
              </v-col>
              <v-col
                class="align-content-end pl-4"
                cols="12"
                md="9"
                tag="dd"
              >
                <div id="mailing-list-course-site-id">
                  {{ canvasSite.canvasSiteId }}
                </div>
              </v-col>
            </v-row>
            <v-row class="mt-2r" no-gutters>
              <v-col
                class="font-weight-medium"
                cols="12"
                md="3"
                tag="dt"
              >
                Description
              </v-col>
              <v-col
                class="pl-4"
                cols="12"
                md="9"
                tag="dd"
              >
                <div id="mailing-list-course-site-code">
                  {{ canvasSite.codeAndTerm }}
                </div>
              </v-col>
            </v-row>
          </v-container>

          <h2 id="mailing-list-header" class="mt-3">Mailing List</h2>
          <v-container
            aria-labelledby="mailing-list-header"
            class="py-3"
            fluid
            tag="dl"
          >
            <v-row no-gutters>
              <v-col
                class="font-weight-medium"
                cols="12"
                md="3"
                tag="dt"
              >
                Name
              </v-col>
              <v-col
                class="pl-4"
                cols="12"
                md="9"
                tag="dd"
              >
                <div id="mailing-list-name">
                  {{ mailingList.name }}@{{ mailingList.domain }}
                </div>
              </v-col>
            </v-row>
            <v-row class="mt-2r" no-gutters>
              <v-col
                class="font-weight-medium"
                cols="12"
                md="3"
                tag="dt"
              >
                Member count
              </v-col>
              <v-col
                class="align-content-end pl-4"
                cols="12"
                md="9"
                tag="dd"
              >
                <div id="mailing-list-member-count">{{ mailingList.membersCount }}</div>
              </v-col>
            </v-row>
            <v-row class="mt-2r" no-gutters>
              <v-col
                class="font-weight-medium"
                cols="12"
                md="3"
                tag="dt"
              >
                Last updated
              </v-col>
              <v-col
                class="align-content-end pl-4"
                cols="12"
                md="9"
                tag="dd"
              >
                <div id="mailing-list-membership-last-updated">
                  <span v-if="get(mailingList, 'populatedAt')">
                    {{ $moment(mailingList.populatedAt).format('MMM D, YYYY') }}
                  </span>
                  <span v-if="!get(mailingList, 'populatedAt')">
                    Never
                  </span>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
      <div class="d-flex flex-wrap justify-end">
        <v-btn
          id="btn-populate-mailing-list"
          class="mt-4 ml-3 w-100 w-sm-auto"
          color="primary"
          :disabled="isUpdating"
          @click="update"
        >
          <span v-if="!isUpdating">Update Memberships{{ hasUpdatedSincePageLoad ? ' Again' : '' }}</span>
          <span v-if="isUpdating">
            <SpinnerWithinButton /> Updating...
          </span>
        </v-btn>
        <v-btn
          id="btn-cancel"
          class="mt-4 ml-3 w-100 w-sm-auto"
          :disabled="isUpdating"
          variant="tonal"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiAccount, mdiAlertCircle, mdiCheck} from '@mdi/js'
import {nextTick, onMounted, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useRouter} from 'vue-router'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {alertScreenReader, oxfordJoin, pluralize, putFocusNextTick} from '@/utils'
import {capitalize, compact, each, get, partition, size} from 'lodash'
import {populateMailingList} from '@/api/mailing-list'
import {useContextStore} from '@/stores/context'
import {useMailingListStore} from '@/stores/mailing-list'

const alerts = ref([])
const alertsLabel = ref(undefined)
const alertTypes = {
  errors: 'error',
  successes: 'success'
}
const contextStore = useContextStore()
const hasUpdatedSincePageLoad = ref(false)
const isUpdating = ref(false)
const mailingListStore = useMailingListStore()
const {canvasSite, mailingList, updateSummary} = storeToRefs(mailingListStore)
const noChangesAlert = ref(undefined)
const openPanelIndex = ref([])
const router = useRouter()

contextStore.loadingStart()

onMounted(() => {
  if (mailingList.value && canvasSite) {
    if (updateSummary.value) {
      showUpdateSummary()
    }
    contextStore.loadingComplete()
  } else {
    router.push({path: '/mailing_list/select_course'})
  }
})

const cancel = () => {
  alertScreenReader('Canceled. Nothing saved.', 'assertive')
  nextTick(router.push({path: '/mailing_list/select_course'}))
}

const showUpdateSummary = () => {
  const actions = ['add', 'remove', 'restore', 'update']
  const count = key => {
    let count = 0
    each(actions, action => count += updateSummary.value[action][key].length)
    return count
  }
  const errorCount = count('errors')
  const successCount = count('successes')
  if (errorCount || successCount) {
    alerts.value = []
    each(['errors', 'successes'], type => {
      each(actions, action => {
        const summary = updateSummary.value[action]
        const emailAddresses = summary[type]
        if (emailAddresses.length) {
          const prefix = type === 'errors' ? `failed to ${action} ` : (action === 'add' ? 'added ' : `${action}d `)
          const message = capitalize(prefix + pluralize('user', emailAddresses.length) + '.')
          const alertType = alertTypes[type]
          alerts.value.push({action, emailAddresses, message, summary, type: alertType})
        }
      })
    })
    const messagesByType = partition(alerts.value, {type: 'error'})
    const errorMessageCount = size(messagesByType[0])
    const successMessageCount = size(messagesByType[1])
    alertsLabel.value = oxfordJoin(compact([
      errorMessageCount ? pluralize('error', errorMessageCount) : null,
      successMessageCount ? pluralize('success message', successMessageCount) : null,
    ]))
    putFocusNextTick('mailing-list-alert-0')
  } else {
    noChangesAlert.value = 'Everything is up-to-date. No changes necessary.'
    alertScreenReader(noChangesAlert.value)
    putFocusNextTick('btn-populate-mailing-list')
  }
}

const update = () => {
  alerts.value = []
  alertsLabel.value = undefined
  noChangesAlert.value = undefined
  alertScreenReader('Updating mailing list.')
  isUpdating.value = true
  const updateTimer = setInterval(() => {
    alertScreenReader('Still processing updates.')
  }, 7000)
  populateMailingList(mailingList.value.id).then(
    data => {
      mailingListStore.setMailingList(data.mailingList)
      mailingListStore.setUpdateSummary(data.summary)
      showUpdateSummary()
    },
    error => {
      alerts.value = [{
        message: error,
        type: 'warning'
      }]
    }
  ).then(() => {
    hasUpdatedSincePageLoad.value = true
  }
  ).finally(() => {
    clearInterval(updateTimer)
    isUpdating.value = false
  })
}
</script>

<style lang="scss" scoped>
.toggle-show-hide {
  text-decoration: none;
  &:hover {
    cursor: pointer;
  }
  &:hover, &:focus {
    text-decoration: underline;
  }
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
button:hover, :focus, :focus-visible {
  .toggle-show-hide {
    text-decoration: underline;
  }
}
ul {
  list-style: none;
}
</style>
