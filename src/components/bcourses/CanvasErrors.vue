<template>
  <v-alert
    id="canvas-error-container"
    aria-live="polite"
    density="compact"
    role="alert"
    type="warning"
  >
    <h1 class="notice-text-header">{{ decamelize(errorType) }}</h1>
    <div v-if="message" class="pt-2">{{ message }}</div>
    <div v-if="!message && errorType === 'unauthorized'" class="pt-2">
      You are unauthorized to use this feature. Please contact bCourses support for further assistance.
    </div>
    <div>
      Please contact
      <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses">bCourses support</OutboundLink> for
      further assistance.
    </div>
  </v-alert>
</template>

<script>
import OutboundLink from '@/components/utils/OutboundLink'
import {decamelize} from '@/utils'

export default {
  name: 'CanvasErrors',
  methods: {decamelize},
  components: {OutboundLink},
  props: {
    errorType: {
      default: 'badRequest',
      required: false,
      type: String
    },
    message: {
      default: undefined,
      required: false,
      type: String
    }
  }
}
</script>
