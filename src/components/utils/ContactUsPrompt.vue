<template>
  <div>
    If you need assistance then please
    <a id="contact-us" href="https://dls.berkeley.edu/services/bcourses-0" target="_blank">contact us</a>.
  </div>
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
