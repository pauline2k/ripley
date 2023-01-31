<template>
  <div :class="{'cc-masthead': $currentUser.isLoggedIn && !isInIframe}">
    <VueAnnouncer class="sr-only" />
    <router-view />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import IFrameMixin from '@/mixins/IFrameMixin'

export default {
  name: 'BaseView',
  mixins: [Context, IFrameMixin]
}
</script>
