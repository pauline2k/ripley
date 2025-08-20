<template>
  <v-list density="compact" :lines="false">
    <template v-for="(tool, index) in tools" :key="index">
      <v-list-item :class="{'pl-0': !config.devAuthEnabled}">
        <template #prepend>
          <v-icon :icon="tool.icon" />
        </template>
        <v-list-item-title>
          <span v-if="tool.disabled" class="font-weight-light">
            {{ tool.title }}
          </span>
          <router-link
            v-if="!tool.disabled"
            :id="getLinkId(tool)"
            class="text-decoration-none"
            :to="tool.path"
          >
            {{ tool.title }}
          </router-link>
        </v-list-item-title>
      </v-list-item>
    </template>
  </v-list>
</template>

<script lang="ts" setup>
import type {PropType} from 'vue'
import type {StandaloneToolOption} from '@/lib/types'
import {useContextStore} from '@/stores/context'

defineProps({
  tools: {
    type: Array as PropType<StandaloneToolOption[]>,
    required: true
  }
})

const config = useContextStore().config

const getLinkId = (tool: StandaloneToolOption) => {
  return `tool-${tool.title.toLowerCase().replace(/[ ]+/g, '-')}-link`
}
</script>
