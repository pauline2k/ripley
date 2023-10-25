<template>
  <div v-if="!isLoading">
    <div class="pb-6 pt-3 px-6">
      <v-card class="elevation-2" color="grey-lighten-4">
        <v-card-title>
          <div class="align-start d-flex ml-2 mt-6">
            <div class="mr-3 mt-1">
              <v-icon
                color="primary"
                :icon="mdiDesktopClassic"
                size="large"
              />
            </div>
            <div>
              <Header1 class="my-0" text="MU-TH-UR 6000" />
              <div class="text-grey-darken-2 text-subtitle-2">
                You cannot edit a job schedule if the job is either enabled or running.
              </div>
            </div>
          </div>
        </v-card-title>
        <v-card-text>
          <v-checkbox
            id="dry-run-checkbox"
            v-model="isDryRun"
            hide-details
            label="Dry run"
          />
          <v-data-table-virtual
            density="compact"
            :headers="headers"
            :items="jobSchedule.jobs"
            item-value="name"
          >
            <template #no-data>
              <div id="message-when-zero-jobs" class="pa-4 text-no-wrap title">
                No jobs
              </div>
            </template>
            <template #item.key="{ item } ">
              <div v-if="!isRunning(item.key)" class="item-run-job">
                <v-btn
                  :id="`run-job-${item.key}`"
                  :aria-label="`Run job ${item.key}`"
                  density="compact"
                  icon
                  size="large"
                  @click="runJob(item)"
                >
                  <v-icon color="success" :icon="mdiPlay" size="large" />
                </v-btn>
              </div>
              <div v-if="isRunning(item.key)" class="item-running-job">
                <v-progress-circular
                  color="warning"
                  indeterminate
                  size="32"
                  width="4"
                />
              </div>
            </template>
            <template #item.name="{ item }">
              <div class="item-name">{{ item.name }}</div>
            </template>
            <template #item.description="{ item }">
              <div class="item-description" v-html="item.description" />
            </template>
            <template #item.schedule="{ item }">
              <div class="align-start d-flex item-schedule">
                <v-btn
                  :id="`edit-job-schedule-${item.key}`"
                  :aria-label="`Edit job schedule ${item.key}`"
                  :disabled="!item.disabled || isRunning(item.key)"
                  icon
                  variant="plain"
                  @click.stop="scheduleEditOpen(item)"
                >
                  <v-icon :icon="mdiPlaylistEdit" />
                </v-btn>
                <div class="pt-3">
                  <label v-if="item.schedule.type === 'day_at'" :for="`edit-job-schedule-${item.key}`">
                    Daily at {{ item.schedule.value.replaceAll(',', ', ') }} (UTC)
                  </label>
                  <label v-if="item.schedule.type !== 'day_at'" :for="`edit-job-schedule-${item.key}`">
                    Every {{ item.schedule.value }} {{ item.schedule.type }}
                  </label>
                </div>
              </div>
            </template>
            <template #item.enabled="{ item }">
              <div class="item-toggle">
                <DisableJobToggle
                  :key="item.disabled"
                  :job="item"
                  :on-change="toggleDisabled"
                />
              </div>
            </template>
          </v-data-table-virtual>
        </v-card-text>
      </v-card>
    </div>
    <div class="pa-6">
      <JobHistory
        :job-history="jobHistory"
        :refreshing="refreshing"
      />
    </div>
    <v-dialog v-model="editJobDialog" max-width="400px" persistent>
      <v-card>
        <v-card-title>
          <span class="headline">{{ get(editJob, 'name') }} Schedule</span>
        </v-card-title>
        <v-card-text>
          <v-container v-if="editJob">
            <v-row>
              <v-col cols="12" sm="6" class="d-flex align-center">
                <label for="job-schedule-select" class="pr-2">Type:</label>
                <select
                  id="job-schedule-select"
                  v-model="editJob.schedule.type"
                  @change="editJob.schedule.value = ''"
                >
                  <option
                    v-for="(item, index) in ['day_at', 'minutes', 'seconds']"
                    :key="index"
                    :value="item"
                  >
                    {{ item }}
                  </option>
                </select>
              </v-col>
              <v-col cols="12" sm="6" class="d-flex align-center">
                <v-text-field
                  v-model="editJob.schedule.value"
                  density="compact"
                  hide-details
                  required
                  :suffix="editJob.schedule.type === 'day_at' ? 'UTC' : ''"
                  :type="editJob.schedule.type === 'day_at' ? 'text' : 'number'"
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
            variant="text"
            @click="scheduleEditSave"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import DisableJobToggle from '@/components/job/DisableJobToggle'
import Header1 from '@/components/utils/Header1.vue'
import JobHistory from '@/components/job/JobHistory'
import {mdiDesktopClassic, mdiPlay, mdiPlaylistEdit} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {cloneDeep, find, get} from 'lodash'
import {getJobHistory, getJobSchedule, setJobDisabled, startJob, updateJobSchedule} from '@/api/job'

export default {
  name: 'Jobs',
  mixins: [Context],
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
    isDryRun: false,
    jobHistory: undefined,
    jobSchedule: undefined,
    refresher: undefined,
    refreshing: false
  }),
  created() {
    this.loadingStart()
    getJobSchedule().then(data => {
      this.jobSchedule = data
      this.refresh(true).then(() => {
        this.$ready()
      })
    })
  },
  unmounted() {
    clearTimeout(this.refresher)
  },
  methods: {
    get,
    isRunning(jobKey) {
      return !!find(this.jobHistory, h => h.jobKey === jobKey && !h.finishedAt)
    },
    refresh(quietly) {
      this.refreshing = true
      return getJobHistory().then(data => {
        this.jobHistory = data
        this.refreshing = false
        if (!quietly) {
          this.alertScreenReader('Job History refreshed')
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
      startJob(job.key, {isDryRun: this.isDryRun}).then(() => {})
      const jobName = find(this.jobSchedule.jobs, ['key', job.key]).name
      console.log(`TODO: this.snackbarOpen(${jobName} job started)`)
    },
    scheduleEditCancel() {
      this.editJob = undefined
      this.editJobDialog = false
      this.alertScreenReader('Cancelled')
    },
    scheduleEditOpen(job) {
      this.editJob = cloneDeep(job)
      this.editJobDialog = true
      this.alertScreenReader(`Opened dialog to edit job ${job.name}`)
    },
    scheduleEditSave() {
      updateJobSchedule(
        this.editJob.id,
        this.editJob.schedule.type,
        this.editJob.schedule.value
      ).then(() => {
        const match = find(this.jobSchedule.jobs, ['id', this.editJob.id])
        match.schedule = this.editJob.schedule
        this.editJob = undefined
        this.editJobDialog = false
        this.alertScreenReader(`Job '${match.name}' was updated.`)
      })
    },
    scheduleRefresh() {
      clearTimeout(this.refresher)
      this.refresher = setTimeout(this.refresh, 5000)
    },
    toggleDisabled(job, isDisabled) {
      setJobDisabled(job.id, isDisabled).then(data => {
        job.disabled = data.disabled
        this.alertScreenReader(`Job '${job.name}' ${job.disabled ? 'disabled' : 'enabled'}`)
      })
    }
  }
}
</script>

<style scoped>
.item-description {
  margin: 36px 0;
  width: 380px;
}
.item-name {
  margin-top: 36px;
  white-space: nowrap;
}
.item-run-job {
  margin-top: 28px;
}
.item-running-job {
  margin: 30px 0 0 2px;
}
.item-schedule {
  margin-top: 24px;
}
.item-toggle {
  margin-top: 16px;
}
</style>
