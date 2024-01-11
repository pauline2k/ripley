<template>
  <div class="icon-blue px-3 mt-3">
    <v-btn
      id="add-user-help-btn"
      aria-controls="page-help-notice"
      :aria-expanded="`${toggle.displayHelp}`"
      block
      class="justify-start"
      :prepend-icon="mdiHelpCircle"
      variant="text"
      @click="toggle.displayHelp = !toggle.displayHelp"
    >
      Need help finding someone?
    </v-btn>
    <v-expand-transition>
      <v-card
        v-show="toggle.displayHelp"
        id="page-help-notice"
        class="user-search-notice rounded-0 mb-4"
        elevation="0"
      >
        <!-- Note: This help text content is also maintained in the canvas-customization.js script -->
        <dl class="mb-0">
          <dt class="user-search-notice-description-term">UC Berkeley Faculty, Staff and Students</dt>
          <dd class="user-search-notice-description">
            UC Berkeley faculty, staff and students <em>(regular and concurrent enrollment)</em> can be found in the
            <OutboundLink href="http://directory.berkeley.edu/">CalNet Directory</OutboundLink>
            and be added to your site using their CalNet UID or official email address.
          </dd>
          <dt class="user-search-notice-description-term">Guests</dt>
          <dd class="user-search-notice-description">
            Peers from other institutions or guests from the community must be sponsored with a
            <OutboundLink href="https://idc.berkeley.edu/guests/">CalNet Guest Account.</OutboundLink>
            Do NOT request a CalNet Guest Account for concurrent enrollment students.
          </dd>
          <dt class="user-search-notice-description-term">More Information</dt>
          <dd class="user-search-notice-description">
            Go to this
            <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0010842">bCourses help page</OutboundLink>
            for more information about adding people to bCourses sites.
          </dd>
        </dl>
      </v-card>
    </v-expand-transition>
  </div>
</template>

<script setup>
import {mdiHelpCircle} from '@mdi/js'
</script>

<script>
import OutboundLink from '@/components/utils/OutboundLink'

export default {
  name: 'NeedHelpFindingSomeone',
  components: {OutboundLink},
  data: () => ({
    toggle: {
      displayHelp: false
    }
  })
}
</script>

<style scoped lang="scss">
.user-search-notice {
  border: 1px solid #d0d0d0;
  padding: 15px;
  .user-search-notice-description-term {
    font-weight: bold;
    margin: 5px 0;
  }
  .user-search-notice-description {
    margin-left: 15px;
  }
}
</style>
