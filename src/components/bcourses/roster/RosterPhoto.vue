<template>
  <v-img
    :id="`student-photo-${student.id}`"
    :alt="`Photo of ${student.firstName} ${student.lastName}`"
    :aria-label="`Photo of ${student.firstName} ${student.lastName}`"
    class="photo"
    cover
    eager
    :lazy-src="photoPlaceholder"
    width="72"
    :src="photoUrl"
    @error="imageError"
    @load="onLoad"
  >
    <template #placeholder>
      <div class="d-flex align-center justify-center fill-height">
        <v-progress-circular
          color="grey-lighten-4"
          indeterminate
        />
      </div>
    </template>
  </v-img>
</template>

<script setup>
import photoPlaceholder from '@/assets/images/roster_photo_placeholder.svg'
import photoUnavailable from '@/assets/images/photo_unavailable.svg'
</script>

<script>
import Context from '@/mixins/Context'
import {trim} from 'lodash'

export default {
  name: 'RosterPhoto',
  mixins: [Context],
  props: {
    onLoad: {
      default: () => {},
      required: false,
      type: Function
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    photoUrl: undefined
  }),
  created() {
    const photoUrl = trim(this.student.photoUrl || '')
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
  min-height: 96px;
}
@media print {
  .photo {
    height: 72px;
  }
}
</style>
