<template>
  <div class="pl-10">
    <pre>{{ profile }}</pre>
  </div>
</template>

<script>
import {getUserProfile} from '@/api/user'

export default {
  name: 'Profile',
  data: () => ({
    profile: undefined
  }),
  created() {
    const uid = this.$_.get(this.$route, 'params.uid')
    getUserProfile(uid).then(data => {
      this.profile = data
      this.$ready()
    })
  }
}
</script>
