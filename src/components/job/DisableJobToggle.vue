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

<script lang="ts" setup>
import {onMounted, ref} from 'vue'

const props = defineProps({
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
})

const enabled = ref(false)

onMounted(() => {
  enabled.value = !props.job.disabled
})
</script>
