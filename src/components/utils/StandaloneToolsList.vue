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

<script>
import Context from '@/mixins/Context.vue'

export default {
  name: 'StandaloneToolsList',
  mixins: [Context],
  props: {
    tools: {
      type: Array,
      required: true
    }
  },
  methods: {
    getLinkId(tool) {
      return `tool-${tool.title.toLowerCase().replace(/[ ]+/g, '-')}-link`
    }
  }
}
</script>
