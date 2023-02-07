<template>
  <span>
    Problem? Question? Email us at
    <a
      id="ripley-support-mailto"
      aria-label="Open new window to send email"
      :class="hrefMailtoClass"
      :href="`mailto:${$config.emailRipleySupport}`"
      target="_blank"
    >
      {{ $config.emailRipleySupport }}
    </a>
  </span>
</template>

<script>
export default {
  name: 'ContactUsPrompt',
  props: {
    hrefMailtoClass: {
      default: undefined,
      required: false,
      type: String
    }
  }
}
</script>
