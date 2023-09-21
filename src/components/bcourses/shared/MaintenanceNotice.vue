<template>
  <v-alert closable color="alert">
    <div class="d-flex">
      <div class="pr-2">
        <v-icon
          icon="mdi-alert"
          aria-hidden="true"
          class="icon-gold"
        />
      </div>
      <div>
        <div class="font-weight-medium pb-1">
          From 8 - 9 AM, you may experience delays of up to 10 minutes before your {{ courseActionVerb }}.
        </div>
        <div id="maintenance-details">
          bCourses performs scheduled maintenance every day between 8 - 9AM, during which time bCourses user
          and enrollment information is synchronized with other campus systems.
          This process may cause delays of up to 10 minutes before your request is completed.
          For more information, check the <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses">bCourses service page</OutboundLink>.
        </div>
      </div>
    </div>
  </v-alert>
</template>

<script>
import OutboundLink from '@/components/utils/OutboundLink'

export default {
  name: 'MaintenanceNotice',
  components: {OutboundLink},
  props: {
    courseActionVerb: {
      required: true,
      type: String
    }
  }
}
</script>
