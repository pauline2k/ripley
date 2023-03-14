<template>
  <div>
    <img
      :id="`student-photo-${student.student_id}`"
      :alt="`Photo of ${student.first_name} ${student.last_name}`"
      :aria-label="`Photo of ${student.first_name} ${student.last_name}`"
      class="photo"
      :src="photoUrl"
      :style="{backgroundImage: `url(${photoUnavailable})`}"
      @error="imageError"
    />
  </div>
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
    if (this.student.photo) {
      this.photoUrl = this.config.apiBaseUrl ? `${this.config.apiBaseUrl}${this.student.photo}` : this.student.photo
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
  background-size: cover;
  height: 96px;
  margin: 0 auto;
  width: auto;
}
@media print {
  .photo {
    height: 147px;
  }
}
</style>
