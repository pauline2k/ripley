<template>
  <v-alert
    id="canvas-error-container"
    aria-atomic="true"
    aria-live="polite"
    color="red-lighten-3"
    density="compact"
    role="alert"
  >
    <h2 class="notice-text-header">{{ decamelize(errorType) }}</h2>
    <div v-if="message" class="pt-2">{{ message }}</div>
    <div v-if="!message && errorType === 'unauthorized'" class="pt-2">
      You are unauthorized to use this feature. Please contact bCourses support for further assistance.
    </div>
    <div class="py-2">
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
