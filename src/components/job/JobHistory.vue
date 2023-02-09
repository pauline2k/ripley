<template>
  <v-card outlined class="elevation-1">
    <v-card-title class="d-flex align-start px-4 py-8">
      <div class="pt-2">
        <h2>
          <v-icon
            class="pb-1"
            :color="$vuetify.theme.dark ? 'white' : 'primary'"
            size="small"
          >
            mdi-history
          </v-icon>
          History
        </h2>
      </div>
      <v-spacer />
      <v-text-field
        v-if="$_.size(jobHistory)"
        v-model="search"
        append-inner-icon="mdi-magnify"
        hide-details
        label="Search History"
        single-line
        variant="underlined"
      />
    </v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        item-value="name"
        :items="jobHistory"
        items-per-page="50"
        :search="search"
      >
        <template #no-data>
          <div id="message-no-job-history" class="pa-4 text-no-wrap title" :colspan="headers.length">
            {{ search ? 'No matching jobs' : 'Job history is empty' }}
          </div>
        </template>
        <template #item.failed="{item}">
          <v-icon v-if="item.raw.finishedAt" :color="item.raw.failed ? 'error' : 'success'">
            {{ item.raw.failed ? 'mdi-exclamation-thick' : 'mdi-check-bold' }}
          </v-icon>
          <v-progress-circular
            v-if="!item.raw.finishedAt"
            :indeterminate="true"
            rotate="5"
            size="24"
            width="4"
            color="orange"
          ></v-progress-circular>
        </template>
        <template #item.startedAt="{item}">
          {{ $moment(item.raw.startedAt).format(dateFormat) }}
        </template>
        <template #item.finishedAt="{item}">
          <span v-if="item.raw.finishedAt">{{ $moment(item.raw.finishedAt).format(dateFormat) }}</span>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'JobHistory',
  mixins: [Context],
  props: {
    jobHistory: {
      required: true,
      type: Array
    },
    refreshing: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    dateFormat: 'dddd, MMMM Do, h:mm:ss a',
    headers: [
      {title: 'Key', key: 'jobKey'},
      {title: 'Status', key: 'failed'},
      {title: 'Started', key: 'startedAt'},
      {title: 'Finished', key: 'finishedAt'}
    ],
    search: undefined
  })
}
</script>
