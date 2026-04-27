<template>
  <div class="align-center d-flex">
    <div aria-hidden="true" class="pr-1">
      <v-icon :icon="mdiChevronLeft" />
    </div>
    <div>
      <a
        aria-label="Back to grade book"
        class="template-back-link"
        :href="`${contextStore.config.canvasApiUrl}/courses/${contextStore.currentUser.canvasSiteId}/grades`"
        target="_top"
      >
        <span aria-hidden="true">Back to Gradebook</span>
      </a>
    </div>
  </div>
</template>

<script setup>
import {mdiChevronLeft} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
</script>
