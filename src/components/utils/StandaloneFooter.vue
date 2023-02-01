<template>
  <footer>
    <v-row v-if="!loading" class="cc-print-hide pb-5 w-100" no-gutters>
      <v-col>
        <v-container class="tangerine-border m-0 p-0 w-100" fluid>
          <v-row
            v-if="$currentUser.isDirectlyAuthenticated || !$currentUser.isLoggedIn"
            class="mt-3 text-secondary"
            no-gutters
          >
            <v-col cols="auto" class="mr-auto">
              <div>
                Berkeley &copy; {{ new Date().getFullYear() }} UC Regents
              </div>
              <div v-if="!isInIframe && includeBuildSummary" class="pt-3 mb-3">
                <div class="d-flex">
                  <div>
                    <h4>Build Summary</h4>
                  </div>
                  <div>
                    <v-btn
                      id="toggle-show-build-summary"
                      aria-controls="build-summary-collapse"
                      variant="text"
                      @click="showBuildSummary = !showBuildSummary"
                    >
                      <v-icon :icon="showBuildSummary ? 'caret-up' : 'caret-down'" />
                    </v-btn>
                  </div>
                </div>
                <v-expansion-panels v-model="showBuildSummary">
                  <v-expansion-panel id="build-summary-collapse">
                    <BuildSummary />
                  </v-expansion-panel>
                </v-expansion-panels>
              </div>
              <div v-if="$currentUser.isBasicAuthEnabled && !$currentUser.isLoggedIn" class="pt-2">
                <div class="d-flex pb-2">
                  <div>
                    <h4>DevAuth</h4>
                  </div>
                  <div>
                    <v-btn
                      id="toggle-show-dev-auth"
                      aria-controls="dev-auth-collapse"
                      variant="link"
                      @click="showDevAuth = !showDevAuth"
                    >
                      <v-icon :icon="showDevAuth ? 'caret-up' : 'caret-down'" />
                    </v-btn>
                  </div>
                </div>
                <v-expansion-panels v-model="showDevAuth">
                  <v-expansion-panel id="dev-auth-collapse">
                    <DevAuth />
                  </v-expansion-panel>
                </v-expansion-panels>
              </div>
            </v-col>
            <v-col cols="auto">
              <div class="d-flex flex-wrap mb-2">
                <div>
                  <OutboundLink href="https://bcourses.berkeley.edu">Return to bCourses</OutboundLink>
                </div>
                <div class="pl-1 pr-1">|</div>
                <div>
                  <OutboundLink href="https://security.berkeley.edu/policy">Usage Policy</OutboundLink>
                </div>
                <div class="pl-1 pr-1">|</div>
                <div>
                  <OutboundLink href="https://www.ets.berkeley.edu/services-facilities/bcourses">About<span class="sr-only"> bCourses</span></OutboundLink>
                </div>
              </div>
            </v-col>
          </v-row>
          <v-row v-if="!isInIframe && $currentUser.isLoggedIn && !$currentUser.isDirectlyAuthenticated" class="border-top pl-3 pt-3 text-secondary w-100" no-gutters>
            <v-col class="pt-1" sm="8">
              <div aria-live="polite" role="alert">
                You are viewing as {{ $currentUser.fullName }} ({{ $currentUser.uid }}),
                <span v-if="$currentUser.firstLoginAt">first logged in on {{ moment($currentUser.firstLoginAt).format('M/D/YY') }}</span>
                <span v-if="!$currentUser.firstLoginAt">who has never logged in to CalCentral</span>
              </div>
            </v-col>
            <v-col sm="4">
              <div class="float-right">
                <v-btn
                  id="stop-viewing-as"
                  class="btn-stop-viewing-as cc-button-blue text-nowrap"
                  size="sm"
                  variant="outline-secondary"
                  @click="stopActAs"
                >
                  Stop viewing as
                </v-btn>
              </div>
            </v-col>
          </v-row>
          <v-row v-if="$config.isVueAppDebugMode" class="w-100" no-gutters>
            <v-col sm="12">
              <div class="text-secondary">
                <span class="font-weight-bolder">Screen-reader alert:</span> {{ screenReaderAlert || '&mdash;' }}
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
  </footer>
</template>

<script>
import BuildSummary from '@/components/utils/BuildSummary'
import Context from '@/mixins/Context'
import DevAuth from '@/components/utils/DevAuth'
import IFrameMixin from '@/mixins/IFrameMixin'
import moment from 'moment'
import OutboundLink from '@/components/utils/OutboundLink'

export default {
  name: 'StandaloneFooter',
  mixins: [Context, IFrameMixin],
  components: {BuildSummary, DevAuth, OutboundLink},
  props: {
    includeBuildSummary: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    showBuildSummary: false,
    showDevAuth: true
  }),
  methods: {
    moment
  }
}
</script>

<style lang="scss" scoped>
h4 {
  font-size: 18px;
}
.btn-stop-viewing-as {
  height: 25px;
  width: 110px;
}
.tangerine-border {
  border-top: 2px solid $cc-color-dark-tangerine;
}
</style>
