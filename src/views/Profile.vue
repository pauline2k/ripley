<template>
  <div class="pl-10">
    <pre>{{ profile }}</pre>
  </div>
</template>

<script setup>
import {get} from 'lodash'
import {onMounted, ref} from 'vue'
import {useRoute} from 'vue-router'
import {getUserProfile} from '@/api/user'
import {useContextStore} from '@/stores/context'

const profile = ref()

onMounted(() => {
  const uid = get(useRoute(), 'params.uid')
  getUserProfile(uid).then(data => {
    profile.value = data
    useContextStore().loadingComplete()
  })
})
</script>
