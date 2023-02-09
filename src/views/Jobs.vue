<template>
  <div v-if="!isLoading" class="pt-2">
    <v-card class="elevation-1 mb-2">
      <v-card-title class="d-flex align-start">
        <div class="pl-2 pt-4">
          <h1>
            <v-icon
              class="pr-3 pb-3"
              color="primary"
              size="small"
            >
              mdi-desktop-classic
            </v-icon>
            <span id="page-title" tabindex="0">MU-TH-UR 6000</span>
          </h1>
        </div>
      </v-card-title>
      <v-card-text>
        <div class="mb-3">
          NOTE: You cannot edit a job schedule if the job is either enabled or running.
        </div>
        <v-data-table-virtual
          :headers="headers"
          :items="jobSchedule.jobs"
          item-value="name"
        >
          <template #no-data>
            <div id="message-when-zero-jobs" class="pa-4 text-no-wrap title" :colspan="headers.length">
              No jobs
            </div>
          </template>
          <template #item.key="{ item } ">
            <v-btn
              v-if="!isRunning(item.raw.key)"
              :id="`run-job-${item.raw.key}`"
              :aria-label="`Run job ${item.raw.key}`"
              icon
              size="large"
              @click="runJob(item.raw)"
            >
              <v-icon color="success" size="large">mdi-play</v-icon>
            </v-btn>
            <v-progress-circular
              v-if="isRunning(item.raw.key)"
              indeterminate
              size="24"
              width="4"
            />
          </template>
          <template #item.description="{ item }">
            <span v-html="item.raw.description"></span>
          </template>
          <template #item.schedule="{ item }">
            <div class="d-flex align-center text-no-wrap">
              <v-btn
                :id="`edit-job-schedule-${item.raw.key}`"
                :aria-label="`Edit job schedule ${item.raw.key}`"
                :disabled="!item.raw.disabled || isRunning(item.raw.key)"
                class="px-0"
                icon
                variant="plain"
                @click.stop="scheduleEditOpen(item.raw)"
              >
                <v-icon>mdi-playlist-edit</v-icon>
              </v-btn>
              <div>
                <span v-if="item.raw.schedule.type === 'day_at'" :for="`edit-job-schedule-${item.raw.key}`">
                  Daily at {{ item.raw.schedule.value }} (UTC)
                </span>
                <span v-if="item.raw.schedule.type !== 'day_at'" :for="`edit-job-schedule-${item.raw.key}`">
                  Every {{ item.raw.schedule.value }} {{ item.raw.schedule.type }}
                </span>
              </div>
            </div>
          </template>
          <template #item.enabled="{ item }">
            <DisableJobToggle :key="item.raw.disabled" :job="item.raw" :on-change="toggleDisabled" />
          </template>
        </v-data-table-virtual>
      </v-card-text>
    </v-card>
    <JobHistory :job-history="jobHistory" :refreshing="refreshing" />
    <v-dialog v-model="editJobDialog" max-width="400px" persistent>
      <v-card>
        <v-card-title>
          <span class="headline">{{ $_.get(editJob, 'name') }} Schedule</span>
        </v-card-title>
        <v-card-text>
          <v-container v-if="editJob">
            <v-row>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editJob.schedule.type"
                  :items="['day_at', 'minutes', 'seconds']"
                  label="Type"
                  required
                  @change="editJob.schedule.value = ''"
                ></v-select>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editJob.schedule.value"
                  required
                  :suffix="editJob.schedule.type === 'day_at' ? 'UTC' : ''"
                  :type="editJob.schedule.type === 'day_at' ? 'time' : 'number'"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="scheduleEditCancel">Cancel</v-btn>
          <v-btn
            color="blue darken-1"
            :disabled="disableScheduleSave"
            text
            @click="scheduleEditSave"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DisableJobToggle from '@/components/job/DisableJobToggle'
import JobHistory from '@/components/job/JobHistory'
import Utils from '@/mixins/Utils'
import {getJobHistory, getJobSchedule, setJobDisabled, startJob, updateJobSchedule} from '@/api/job'

export default {
  name: 'Jobs',
  mixins: [Context, Utils],
  components: {
    DisableJobToggle,
    JobHistory
  },
  data: () => ({
    disableScheduleSave: false,
    editJob: undefined,
    editJobDialog: false,
    headers: [
      {key: 'key', title: ''},
      {key: 'name', title: 'Name'},
      {key: 'description', title: 'Description'},
      {key: 'schedule', title: 'Schedule'},
      {key: 'enabled', title: 'Enabled'}
    ],
    jobHistory: undefined,
    jobSchedule: undefined,
    refresher: undefined,
    refreshing: false
  }),
  created() {
    this.$loading()
    getJobSchedule().then(data => {
      this.jobSchedule = data
      this.refresh(true).then(() => {
        this.$ready('MU-TH-UR 6000')
      })
    })
  },
  unmounted() {
    clearTimeout(this.refresher)
  },
  methods: {
    isRunning(jobKey) {
      return !!this.$_.find(this.jobHistory, h => h.jobKey === jobKey && !h.finishedAt)
    },
    refresh(quietly) {
      this.refreshing = true
      return getJobHistory().then(data => {
        this.jobHistory = data
        this.refreshing = false
        if (!quietly) {
          this.$announcer.polite('Job History refreshed')
        }
        this.scheduleRefresh()
      })
    },
    runJob(job) {
      this.jobHistory.unshift({
        jobKey: job.key,
        failed: false,
        startedAt: this.$moment()
      })
      startJob(job.key).then(() => {})
      const jobName = this.$_.find(this.jobSchedule.jobs, ['key', job.key]).name
      // TODO: this.snackbarOpen(`${jobName} job started`)
    },
    scheduleEditCancel() {
      this.editJob = undefined
      this.editJobDialog = false
      this.$announcer.polite('Cancelled')
    },
    scheduleEditOpen(job) {
      this.editJob = this.$_.cloneDeep(job)
      this.editJobDialog = true
      this.$announcer.polite(`Opened dialog to edit job ${job.name}`)
    },
    scheduleEditSave() {
      updateJobSchedule(
        this.editJob.id,
        this.editJob.schedule.type,
        this.editJob.schedule.value
      ).then(() => {
        const match = this.$_.find(this.jobSchedule.jobs, ['id', this.editJob.id])
        match.schedule = this.editJob.schedule
        this.editJob = undefined
        this.editJobDialog = false
        this.$announcer.polite(`Job '${match.name}' was updated.`)
      })
    },
    scheduleRefresh() {
      clearTimeout(this.refresher)
      this.refresher = setTimeout(this.refresh, 5000)
    },
    toggleDisabled(job, isDisabled) {
      setJobDisabled(job.id, isDisabled).then(data => {
        job.disabled = data.disabled
        this.$announcer.polite(`Job '${job.name}' ${job.disabled ? 'disabled' : 'enabled'}`)
      })
    }
  }
}
</script>
