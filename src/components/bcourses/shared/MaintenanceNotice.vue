<template>
  <div class="alert">
    <button
      id="maintenance-notice-button"
      class="button-link template-canvas-maintenance-notice-button"
      aria-controls="maintenance-details"
      :aria-expanded="`${!maintenanceCollapsed}`"
      aria-haspopup="true"
      @click="maintenanceCollapsed = !maintenanceCollapsed"
    >
      <v-icon
        :icon="maintenanceCollapsed ? 'mdi-menu-right' : 'mdi-menu-down'"
        class="pr-1"
        aria-hidden="true"
        size="large"
        start
      />
      <v-icon
        icon="mdi-alert"
        class="icon-gold mr-0"
        aria-hidden="true"
        start
      />
      <span class="template-canvas-maintenance-notice-text">
        From 8 - 9 AM, you may experience delays of up to 10 minutes before your {{ courseActionVerb }}.
      </span>
    </button>
    <div id="maintenance-details" aria-live="polite">
      <div v-if="!maintenanceCollapsed" class="template-canvas-maintenance-notice-details">
        <p>
          bCourses performs scheduled maintenance every day between 8-9AM, during which time bCourses user
          and enrollment information is synchronized with other campus systems.
          This process may cause delays of up to 10 minutes before your request is completed.
          For more information, check the <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses">bCourses service page</OutboundLink>.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import OutboundLink from '@/components/utils/OutboundLink'

export default {
  name: 'MaintenanceNotice',
  components: {OutboundLink},
  props: {
    courseActionVerb: {
      type: String,
      default: ''
    }
  },
  data: () => ({
    maintenanceCollapsed: true
  })
}
</script>

<style scoped lang="scss">
button.template-canvas-maintenance-notice-button {
  &, &:hover, &:focus {
    color: $color-alert-foreground;
    text-decoration: none;
  }
}
.template-canvas-maintenance-notice-details {
  font-size: 14px;
  font-weight: normal;
  margin: 10px 26px 0;

  p {
    margin-bottom: 5px;
  }
}
</style>
