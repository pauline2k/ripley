<template>
  <v-card class="elevation-2" color="grey-lighten-4" outlined>
    <v-card-title>
      <div class="align-start d-flex py-3">
        <h2 class="ml-2 mt-3">
          <v-icon
            class="mr-2"
            :color="theme.global.current.value.dark ? 'white' : 'primary'"
            :icon="mdiHistory"
            size="large"
          />
          Job History
        </h2>
        <v-spacer />
        <v-text-field
          v-if="size(jobHistory)"
          v-model="search"
          :append-inner-icon="mdiMagnify"
          class="bg-white"
          hide-details
          label="Search History"
          single-line
          variant="outlined"
        />
      </div>
    </v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        item-value="id"
        :items="jobHistory"
        density="compact"
        items-per-page="10"
        :search="search"
        show-expand
      >
        <template #no-data>
          <div id="message-no-job-history" class="pa-4 text-no-wrap title">
            {{ search ? 'No matching jobs' : 'Job history is empty' }}
          </div>
        </template>
        <template #item.jobKey="{item}">
          <div class="font-size-15 py-2 text-grey-darken-2">
            {{ item.jobKey }}
          </div>
        </template>
        <template #item.failed="{item}">
          <div class="py-2">
            <v-icon
              v-if="item.finishedAt"
              :color="item.failed ? 'error' : 'success'"
              :icon="item.failed ? mdiAlert : mdiCheckCircle"
            />
            <div v-if="!item.finishedAt">
              <v-progress-circular
                :indeterminate="true"
                rotate="5"
                size="18"
                width="4"
                color="orange"
              />
            </div>
          </div>
        </template>
        <template #item.startedAt="{item}">
          <div class="py-2">
            {{ formatIsoDate(item.startedAt) }}
          </div>
        </template>
        <template #item.finishedAt="{item}">
          <div v-if="item.finishedAt" class="py-2">
            {{ formatIsoDate(item.finishedAt) }}
          </div>
        </template>
        <template #expanded-row="{item}">
          <tr class="bg-secondary">
            <td colspan="5" class="px-4 py-2">
              <div><strong>Job result</strong></div>
              <div>{{ item.result || 'No details.' }}</div>
            </td>
          </tr>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script lang="ts" setup>
import type {PropType} from 'vue'
import {mdiAlert, mdiCheckCircle, mdiHistory, mdiMagnify} from '@mdi/js'
import {ref} from 'vue'
import {size} from 'lodash'
import {useTheme} from 'vuetify'
import moment from 'moment'
import type {JobHistory} from '@/lib/types'

defineProps({
  jobHistory: {
    required: true,
    type: Array as PropType<JobHistory[]>
  },
  refreshing: {
    required: true,
    type: Boolean
  }
})

const headers = [
  {title: '', key: 'jobKey', sortable: false},
  {title: 'Status', key: 'failed'},
  {title: 'Started', key: 'startedAt'},
  {title: 'Finished', key: 'finishedAt'}
]
const search = ref()
const theme = useTheme()

const formatIsoDate = (isoDate: string) => moment(isoDate).format('ddd, MMM Do, h:mm:ss A')
</script>
