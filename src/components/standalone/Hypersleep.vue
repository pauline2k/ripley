<template>
  <v-card
    class="elevation-2"
    color="grey-lighten-4"
    outlined
  >
    <v-card-title>
      <div class="align-start d-flex py-3">
        <h2 class="ml-2 mt-3">
          <div class="align-center d-flex">
            <div class="pr-2">
              <v-icon
                :color="$vuetify.theme.dark ? 'white' : 'primary'"
                :icon="mdiBed"
                size="large"
              />
            </div>
            <h2>Hypersleep</h2>
          </div>
        </h2>
      </div>
    </v-card-title>
    <v-card-text>
      <v-switch
        :id="`hypersleep-enabled`"
        v-model="enabled"
        :aria-label="`Hypersleep is ${enabled ? 'enabled' : 'disabled'}`"
        color="success"
        density="compact"
        hide-details
        :label="enabled ? 'Enabled' : 'Disabled'"
        @change="toggleHypersleep(enabled)"
      />
    </v-card-text>
  </v-card>
</template>

<script setup>
import {mdiBed} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {setHypersleep} from '@/api/configuration'
import {useContextStore} from '@/stores/context'

export default {
  name: 'Hypersleep',
  mixins: [Context],
  data: () => ({
    enabled: undefined
  }),
  created() {
    this.enabled = this.config.hypersleep
  },
  methods: {
    toggleHypersleep(isEnabled) {
      setHypersleep(isEnabled).then(data => {
        this.enabled = data.hypersleep
        useContextStore().setHypersleep(this.enabled)
        this.alertScreenReader(`Hypersleep ${this.enabled ? 'enabled' : 'disabled'}`)
      })
    }
  }
}
</script>
