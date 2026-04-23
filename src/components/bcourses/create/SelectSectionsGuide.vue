<template>
  <v-alert
    class="mt-2"
    close-label="Hide help"
    role="none"
    @click:close="onCloseHelp"
  >
    <div class="d-flex">
      <v-icon
        class="mr-2r page-help-notice-icon text-medium-emphasis"
        :icon="mdiHelpCircleOutline"
      />
      <div>
        <div class="font-weight-medium">
          Need help deciding which official sections to select?
        </div>
        <p class="mt-2">
          If you have a course with multiple sections, you will need to decide whether you want to:
          <ol class="my-2 ml-4r mr-2">
            <li>
              Create one, single course site which includes official sections for both your primary and secondary sections, or
            </li>
            <li>
              Create multiple course sites, perhaps with one for each section, or
            </li>
            <li>
              Create separate course sites based on instruction mode.
              <OutboundLink
                href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0010732#instructionmode"
                period-terminated
              >
                Learn more about instruction modes in bCourses
              </OutboundLink>
            </li>
          </ol>
        </p>
      </div>
    </div>
  </v-alert>
</template>

<script setup>
import OutboundLink from '@/components/utils/OutboundLink'
import {mdiHelpCircleOutline} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {get, size} from 'lodash'
import {alertScreenReader, putFocusNextTick} from '@/utils'

export default {
  name: 'SelectSectionsGuide',
  mixins: [Context],
  methods: {
    onCloseHelp() {
      alertScreenReader('help hidden')
      putFocusNextTick(size(this.coursesList) ? `sections-course-${get(this.coursesList, '0.slug')}-btn` : 'page-create-course-site-cancel')
    }
  }
}
</script>
