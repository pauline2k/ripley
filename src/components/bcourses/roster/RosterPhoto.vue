<template>
  <v-img
    :id="`student-photo-${student.id}`"
    :alt="`Photo of ${student.firstName} ${student.lastName}`"
    :aria-label="`Photo of ${student.firstName} ${student.lastName}`"
    class="photo"
    cover
    width="72"
    :src="photoUrl"
    @error="imageError"
  />
</template>

<script setup>
import photoUnavailable from '@/assets/images/photo_unavailable.svg'
</script>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'RosterPhoto',
  mixins: [Context],
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    photoUrl: undefined
  }),
  created() {
    const photoUrl = this.$_.trim(this.student.photoUrl || '')
    if (photoUrl) {
      this.photoUrl = photoUrl.startsWith('http') ? photoUrl : `${this.config.apiBaseUrl}${photoUrl}`
    } else {
      this.imageError()
    }
  },
  methods: {
    imageError() {
      this.photoUrl = photoUnavailable
    }
  }
}
</script>

<style scoped>
.photo {
  margin: 0 auto;
}
@media print {
  .photo {
    height: 147px;
  }
}
</style>
