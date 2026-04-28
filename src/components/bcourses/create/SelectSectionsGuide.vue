<template>
  <v-alert
    class="mt-2"
    density="compact"
    role="none"
  >
    <div class="d-flex">
      <v-icon
        class="mr-1r mt-2 page-help-notice-icon text-medium-emphasis"
        :icon="mdiHelpCircleOutline"
      />
      <div class="pa-1 w-100">
        <v-btn
          id="toggle-help-notice-btn"
          :append-icon="isExpanded ? mdiChevronDown : mdiChevronRight"
          aria-controls="official-sections-help-notice"
          :aria-expanded="isExpanded"
          block
          class="font-weight-medium justify-space-between px-2"
          density="compact"
          :ripple="false"
          size="large"
          variant="text"
          @click="isExpanded = !isExpanded"
        >
          Need help deciding which official sections to select?
        </v-btn>
        <v-expand-transition>
          <p v-show="isExpanded" id="official-sections-help-notice" class="mt-2">
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
        </v-expand-transition>
      </div>
    </div>
  </v-alert>
</template>

<script setup>
import {ref} from 'vue'
import OutboundLink from '@/components/utils/OutboundLink'
import {mdiChevronDown, mdiChevronRight, mdiHelpCircleOutline} from '@mdi/js'

const isExpanded = ref(true)
</script>
