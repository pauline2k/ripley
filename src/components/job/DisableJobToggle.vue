<template>
  <v-switch
    :id="`job-${job.key}-enabled`"
    v-model="enabled"
    :aria-label="`Job ${job.name} is ${enabled ? 'enabled' : 'disabled'}`"
    color="success"
    density="compact"
    hide-details
    :label="enabled ? 'Enabled' : 'Disabled'"
    @change="onChange(job, !enabled)"
  />
</template>

<script>
export default {
  name: 'DisableJobToggle',
  props: {
    isRunning: {
      required: true,
      type: Boolean
    },
    job: {
      required: true,
      type: Object
    },
    onChange: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    enabled: undefined
  }),
  created() {
    this.enabled = !this.job.disabled
  }
}
</script>
