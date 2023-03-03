<template>
  <a :id="id || `link-to-${href.replace(/\W/g, '')}`" :href="href" target="_blank">
    <slot />
    <span class="outbound-link visuallyhidden print-hide"> (link opens new browser tab)</span>
  </a>
</template>

<script>
export default {
  name: 'OutboundLink',
  props: {
    href: {
      type: String,
      required: true
    },
    id: {
      default: undefined,
      type: String,
      required: false
    }
  }
}
</script>
