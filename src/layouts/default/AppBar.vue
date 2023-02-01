<template>
  <v-app-bar flat>
    <v-app-bar-title>
      <div class="align-center d-flex justify-space-between">
        <div>
          <BuildSummary />
        </div>
        <div class="float-right mr-3 text-body-2" cols="6">
          <span
            v-if="$config.isVueAppDebugMode"
            class="font-weight-bolder text-secondary"
          >
            {{ screenReaderAlert || '&mdash;' }}
          </span>
          <span>
            Berkeley &copy; {{ new Date().getFullYear() }} UC Regents
          </span>
        </div>
      </div>
    </v-app-bar-title>
  </v-app-bar>
</template>

<script>
import BuildSummary from '@/components/utils/BuildSummary'
import Context from '@/mixins/Context'
import moment from 'moment'

export default {
  name: 'AppBar',
  mixins: [Context],
  components: {BuildSummary},
  props: {
    includeBuildSummary: {
      required: false,
      type: Boolean
    }
  },
  methods: {
    moment
  }
}
</script>
