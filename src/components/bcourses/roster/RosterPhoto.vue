<template>
  <div class="photo-outer">
    <a
      :id="`student-profile-url-${student.studentId}`"
      class="text-decoration-none"
      :href="student.profileUrl || `${config.apiBaseUrl}/redirect/canvas/${currentUser.canvasSiteId}/user/${student.uid}`"
      target="_top"
    >
      <div class="sr-only">Student profile page</div>
      <v-img
        :id="`student-photo-${student.id}`"
        :alt="`Photo of ${student.firstName} ${student.lastName}`"
        :aria-label="`Photo of ${student.firstName} ${student.lastName}`"
        class="photo"
        :class="showOnePhotoPerPage ? 'photo-one-per-page' : ''"
        eager
        :lazy-src="photoPlaceholder"
        transition="none"
        :src="photoSrc"
        @error="imageError"
        @load="onLoad"
      />
    </a>
  </div>
</template>

<script setup>
import photoPlaceholder from '@/assets/images/roster_photo_placeholder.svg'
</script>

<script>
import Context from '@/mixins/Context'
import photoUnavailable from '@/assets/images/photo_unavailable.svg'

export default {
  name: 'RosterPhoto',
  mixins: [Context],
  props: {
    onLoad: {
      default: () => {},
      required: false,
      type: Function
    },
    photoUrl: {
      default: undefined,
      required: false,
      type: String
    },
    showOnePhotoPerPage: {
      required: true,
      type: Boolean
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    imageErrored: false
  }),
  computed: {
    photoSrc() {
      if (this.imageErrored) {
        return photoUnavailable
      } else {
        return this.photoUrl
      }
    }
  },
  methods: {
    imageError() {
      this.onLoad()
      this.imageErrored = true
    }
  }
}
</script>

<style scoped>
.photo {
  height: 96px;
  width: 72px;
}
.photo-outer {
  display: flex;
  justify-content: center;
}
@media print {
  .photo {
    height: 130px;
    width: auto;
  }
  .photo-one-per-page {
    height: 400px;
  }
}
</style>
