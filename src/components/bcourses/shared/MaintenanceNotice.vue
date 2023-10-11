<template>
  <v-alert
    id="maintenance-notice"
    aria-labelledby="maintenance-notice-label"
    closable
    close-label="Hide notice"
    color="alert"
    role="status"
    @click:close="onClose"
  >
    <div class="d-flex">
      <div class="pr-2">
        <v-icon
          icon="mdi-alert"
          aria-hidden="true"
          class="icon-gold"
        />
      </div>
      <div>
        <div class="font-weight-bold pb-1">
          <span id="maintenance-notice-label" class="sr-only">Maintenance notice </span><span class="sr-only">closeable alert.</span>
          From 8 -<span class="sr-only">to</span> 9 AM, you may experience delays of up to 10 minutes before your {{ courseActionVerb }}.
        </div>
        <div id="maintenance-details">
          bCourses performs scheduled maintenance every day from 8 -<span class="sr-only">to</span> 9AM, during which time bCourses user
          and enrollment information is synchronized with other campus systems.
          This process may cause delays of up to 10 minutes before your request is completed.
          For more information, check the <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses">bCourses service page</OutboundLink>.
        </div>
      </div>
    </div>
  </v-alert>
</template>

<script>
import Context from '@/mixins/Context'
import {nextTick} from 'vue'
import OutboundLink from '@/components/utils/OutboundLink'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'MaintenanceNotice',
  components: {OutboundLink},
  mixins: [Context],
  props: {
    courseActionVerb: {
      required: true,
      type: String
    }
  },
  methods: {
    onClose() {
      this.alertScreenReader('notice hidden')
      nextTick(() => putFocusNextTick('page-title'))
    }
  }
}
</script>
