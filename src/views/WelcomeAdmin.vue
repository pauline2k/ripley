<template>
  <v-container
    v-if="!isLoading"
    class="h-100 mb-2 pt-1 px-6"
    fill-height
    fluid
    :style="{backgroundImage: `url(${deepSpace})`, backgroundRepeat: 'repeat'}"
  >
    <v-row class="sr-only">
      <v-col>
        <Header1 id="page-title" text="Welcome" />
      </v-col>
    </v-row>
    <v-row v-if="showLatestJobAlert" class="pt-3" no-gutters>
      <v-col>
        <v-alert
          v-model="showLatestJobAlert"
          closable
          color="white"
          density="compact"
          role="alert"
          rounded
          variant="outlined"
        >
          <template #title>
            <div class="align-center d-flex">
              <div class="mr-2">
                <SpinnerWithinButton
                  v-if="latestJob.isRunning"
                  class="mb-1"
                  color="green"
                  :size="20"
                />
                <v-icon
                  v-if="!latestJob.isRunning"
                  :color="latestJob.iconColor"
                  :icon="latestJob.icon"
                />
              </div>
              <div>
                {{ latestJob.description }}
              </div>
            </div>
          </template>
        </v-alert>
      </v-col>
    </v-row>
    <v-row
      align="start"
      :class="{'mt-1': showLatestJobAlert}"
      justify="center"
    >
      <v-col>
        <v-card v-if="jobSchedule">
          <v-card-title>
            <div class="align-start d-flex ml-2 mt-6">
              <div class="mr-4 mt-1">
                <v-icon
                  color="primary"
                  :icon="mdiDesktopClassic"
                  size="large"
                />
              </div>
              <div>
                <h2>MU-TH-UR 6000</h2>
                <div class="text-grey-darken-2 text-subtitle-2">
                  A job schedule can be modified when the job is disabled.
                </div>
                <v-checkbox
                  id="dry-run-checkbox"
                  v-model="isDryRun"
                  class="dry-run-checkbox"
                  hide-details
                  label="Dry run"
                />
              </div>
              <v-spacer />
              <div>
                <v-img
                  id="ripley-with-cat-img"
                  alt="Ripley with cat"
                  aria-label="Ripley with cat"
                  class="float-right rounded-lg"
                  :src="ripleyWithCat"
                  width="160"
                />
              </div>
            </div>
          </v-card-title>
          <v-card-text>
            <div v-if="jobSchedule.jobs.length">
              <div
                v-for="(job, index) in jobSchedule.jobs"
                :key="job.id"
                class="pa-2"
                :class="{'bg-striped-row': index % 2}"
              >
                <div class="align-center d-flex flex-wrap">
                  <div class="pr-3">
                    <div v-if="!isRunning(job.key)">
                      <v-btn
                        :id="`run-job-${job.key}`"
                        :aria-label="`Run job ${job.key}`"
                        density="compact"
                        icon
                        size="large"
                        @click="runJob(job)"
                      >
                        <v-icon color="success" :icon="mdiPlay" size="large" />
                      </v-btn>
                    </div>
                    <div v-if="isRunning(job.key)">
                      <v-progress-circular
                        color="warning"
                        indeterminate
                        size="32"
                        width="4"
                      />
                    </div>
                  </div>
                  <div>
                    <h3>
                      <label :for="`run-job-${job.key}`">{{ job.name }}</label>
                    </h3>
                  </div>
                  <div class="ml-auto pr-3">
                    <DisableJobToggle
                      :key="job.disabled"
                      class="float-right"
                      :job="job"
                      :is-running="isRunning(job.key)"
                      :on-change="toggleDisabled"
                    />
                  </div>
                </div>
                <div class="ml-12">
                  <div class="pr-2" v-html="job.description" />
                  <div class="align-start d-flex mt-1">
                    <div class="mb-1">
                      <label v-if="job.schedule.type === 'day_at'" :for="`edit-job-schedule-${job.key}`">
                        Daily at {{ job.schedule.value.replaceAll(',', ', ') }} (UTC)
                      </label>
                      <label v-if="job.schedule.type !== 'day_at'" :for="`edit-job-schedule-${job.key}`">
                        Every {{ job.schedule.value }} {{ job.schedule.type }}
                      </label>
                    </div>
                    <div class="edit-job-schedule-btn">
                      <v-btn
                        :id="`edit-job-schedule-${job.key}`"
                        :aria-label="`Edit job schedule ${job.key}`"
                        :disabled="!job.disabled || isRunning(job.key)"
                        icon
                        variant="text"
                        @click.stop="scheduleEditOpen(job)"
                      >
                        <v-icon :icon="mdiPlaylistEdit" />
                      </v-btn>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="!jobSchedule.jobs.length" id="message-when-zero-jobs" class="pa-4 text-no-wrap title">
              No jobs
            </div>
          </v-card-text>
        </v-card>
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
                        v-for="(option, index) in ['day_at', 'minutes', 'seconds']"
                        :key="index"
                        :value="option"
                      >
                        {{ option }}
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
                    />
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
      </v-col>
      <v-col>
        <div class="pb-1">
          <ToolPortfolio :v-card-class="`pl-2 elevation-0`" />
        </div>
        <JobHistory
          v-if="jobHistory"
          class="mt-6"
          :job-history="jobHistory"
          :refreshing="refreshing"
        />
        <NostromoCrew class="mt-6" />
        <Hypersleep class="mt-6" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import deepSpace from '@/assets/images/deep-space-background-tile.png'
import DisableJobToggle from '@/components/job/DisableJobToggle'
import Header1 from '@/components/utils/Header1.vue'
import Hypersleep from '@/components/standalone/Hypersleep'
import JobHistory from '@/components/job/JobHistory'
import NostromoCrew from '@/components/standalone/NostromoCrew'
import ripleyWithCat from '@/assets/images/ripley-with-cat.png'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import ToolPortfolio from '@/components/standalone/ToolPortfolio.vue'
import {mdiDesktopClassic, mdiPlay, mdiPlaylistEdit} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {cloneDeep, concat, each, filter, find, get, isNil, partition} from 'lodash'
import {getJobHistory, getJobSchedule, setJobDisabled, startJob, updateJobSchedule} from '@/api/job'
import {mdiMessageAlert, mdiStar} from '@mdi/js'

export default {
  name: 'Welcome',
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
    refreshing: false,
    showLatestJobAlert: undefined
  }),
  computed: {
    latestJob() {
      let description
      let icon
      let iconColor
      const runningJobs = filter(this.jobHistory, ['finishedAt', null]) || []
      if (runningJobs.length) {
        description = ''
        each(runningJobs, job => {
          description += `${job.jobKey} started ${this.$moment(job.startedAt).fromNow()}. `
        })
      } else {
        const job = this.jobHistory[0]
        const finishedAt = this.$moment(job.finishedAt).fromNow()
        description = `${job.jobKey} ${job.failed ? 'failed' : 'finished'} ${finishedAt}.`
        icon = job.failed ? mdiMessageAlert : mdiStar
        iconColor = job.failed ? 'error' : 'green'
      }
      return {
        description,
        icon,
        iconColor,
        isRunning: runningJobs.length
      }
    }
  },
  created() {
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
        const partitions = partition(data, j => j.finishedAt)
        this.jobHistory = concat(partitions[1], partitions[0])
        if (isNil(this.showLatestJobAlert) && this.jobHistory.length > 1) {
          // Set this flag only once: when jobHistory is non-empty. The flag is set to false when user closes the alert.
          this.showLatestJobAlert = true
        }
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
.bg-striped-row {
  background-color: #d9edf7;
}
.dry-run-checkbox {
  margin: -10px 0 0 -10px;
}
.edit-job-schedule-btn {
  margin-top: -12px;
}
</style>
