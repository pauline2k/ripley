<template>
  <router-view id="content" tabindex="-1" />
</template>

<script setup>
import {onBeforeUnmount, onMounted} from 'vue'
import {iframePostMessage, isInIframe} from '@/utils'

onMounted(() => {
  if (isInIframe) {
    setInterval(iframeUpdateHeight, 250)
  }
})

onBeforeUnmount(() => {
  if (isInIframe) {
    clearInterval(iframeUpdateHeight)
  }
})

/**
 * Update the iframe height on a regular basis to avoid embedded scrollbars on
 * bCourses LTI tools. The message is formatted to be received by a listener
 * in Canvas's public/javascripts/tool_inline.js file; unless it exceeds the
 * Canvas 5000px limit, in which case our own listener handles it.
 */
const iframeUpdateHeight = () => {
  const mainElement = document.getElementById('ripley-main')
  if (mainElement) {
    const frameHeight = mainElement.scrollHeight
    const messageSubject = frameHeight > 5000 ? 'changeParent' : 'lti.frameResize'
    const message = {
      subject: messageSubject,
      height: frameHeight
    }
    iframePostMessage(JSON.stringify(message))
  }
}
</script>
