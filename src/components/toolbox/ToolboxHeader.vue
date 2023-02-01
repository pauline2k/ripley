<template>
  <v-row v-if="!isInIframe" class="bg-header" no-gutters>
    <v-col sm="8">
      <div class="header-text mt-1 pl-3 pt-2">
        ETS bCourses Utilities
      </div>
    </v-col>
    <v-col cols="auto" sm="4">
      <div class="mt-1 pr-3">
        <v-btn
          id="log-out"
          class="float-right text-white"
          variant="link"
          @click="exit"
        >
          Log out
        </v-btn>
      </div>
    </v-col>
  </v-row>
</template>

<script>
import Context from '@/mixins/Context'
import IFrameMixin from '@/mixins/IFrameMixin'
import {logOut} from '@/api/auth'

export default {
  name: 'ToolboxHeader',
  mixins: [Context, IFrameMixin],
  methods: {
    exit() {
      this.$announcer.polite('Logging out.')
      logOut().then(() => {
        window.location.href = '/'
      })
    }
  }
}
</script>

<style scoped>
.bg-header {
  background: #002e5b;
}
.header-text {
  color: #f1a91e;
  display: inline-block;
  font-weight: bold;
  line-height: 1.6;
}
</style>
