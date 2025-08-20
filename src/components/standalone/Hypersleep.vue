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
                :color="theme.global.current.value.dark ? 'white' : 'primary'"
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

<script lang="ts" setup>
import {mdiBed} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useTheme} from 'vuetify'
import {setHypersleep} from '@/api/configuration'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const enabled = ref(false)
const theme = useTheme()

onMounted(() => {
  enabled.value = contextStore.config.hypersleep
})

const toggleHypersleep = (isEnabled: boolean) => {
  setHypersleep(isEnabled).then(data => {
    enabled.value = data.hypersleep
    contextStore.setHypersleep(enabled.value)
    contextStore.alertScreenReader(`Hypersleep ${enabled.value ? 'enabled' : 'disabled'}`)
  })
}
</script>
