<template>
  <v-alert
    class="mt-2"
    closable
    close-label="Hide help"
    @click:close="onCloseHelp"
  >
    <div class="d-flex">
      <div class="pr-2">
        <v-icon
          class="left page-help-notice-icon"
          color="grey"
          :icon="mdiHelpCircleOutline"
        />
      </div>
      <div>
        <div class="font-weight-medium">
          Need help deciding which official sections to select?
        </div>
        If you have a course with multiple sections, you will need to decide whether you want to:
        <div class="mt-1">
          1. Create one, single course site which includes official sections for both your primary and secondary sections, or
        </div>
        <div>
          2. Create multiple course sites, perhaps with one for each section, or
        </div>
        <div>
          3. Create separate course sites based on instruction mode.
          <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0010732#instructionmode">
            Learn more about instruction modes in bCourses.
          </OutboundLink>
        </div>
      </div>
    </div>
  </v-alert>
</template>

<script setup>
import OutboundLink from '@/components/utils/OutboundLink'
import {mdiHelpCircleOutline} from '@mdi/js'
</script>

<script>
import {get, size} from 'lodash'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'SelectSectionsGuide',
  methods: {
    onCloseHelp() {
      this.alertScreenReader('help hidden')
      putFocusNextTick(size(this.coursesList) ? `sections-course-${get(this.coursesList, '0.slug')}-btn` : 'page-create-course-site-cancel')
    }
  }
}
</script>
