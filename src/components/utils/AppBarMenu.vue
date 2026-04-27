<template>
  <v-menu>
    <template #activator="{ props }">
      <v-btn
        class="ma-1"
        variant="outlined"
        v-bind="props"
      >
        {{ currentUser.firstName || currentUser.uid }}
      </v-btn>
    </template>
    <v-list class="pt-3">
      <v-list-item-action
        v-for="option in options"
        :key="option.id"
      >
        <v-btn
          :id="option.id"
          variant="plain"
          @click="option.onClick"
        >
          {{ option.label }}
        </v-btn>
      </v-list-item-action>
    </v-list>
  </v-menu>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import {useRouter} from 'vue-router'
import {logOut} from '@/api/auth'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const options = ref([])
const router = useRouter()

onMounted(() => {
  if (currentUser.canAccessStandaloneView) {
    addOption('my-profile', 'My Profile', goProfile)
    if (currentUser.isAdmin) {
      addOption('acheron-lv-426', 'Acheron (LV-426)', goAcheron)
    }
  }
  addOption('log-out', 'Log Out', onLogOut)
})

const addOption = (id, label, onClick) => {
  options.value.push({id, label, onClick})
}

const goAcheron = () => {
  router.push({path: '/acheron'})
}

const goProfile = () => {
  router.push({path: `/profile/${currentUser.uid}`})
}

const onLogOut = () => {
  contextStore.loadingStart()
  logOut().then(data => window.location.href = data.casLogoutUrl)
}
</script>
