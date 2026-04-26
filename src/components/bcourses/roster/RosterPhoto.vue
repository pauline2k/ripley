<template>
  <div class="photo-outer">
    <a
      :id="`student-profile-url-${student.studentId}`"
      class="text-decoration-none"
      :href="student.profileUrl || `${contextStore.config.apiBaseUrl}/redirect/canvas/${contextStore.currentUser.canvasSiteId}/user/${student.uid}`"
      target="_top"
    >
      <v-img
        :id="`student-photo-${student.id}`"
        :alt="`${student.firstName} ${student.lastName}`"
        class="photo"
        :class="showOnePhotoPerPage ? 'photo-one-per-page' : ''"
        eager
        :lazy-src="photoPlaceholder"
        transition="none"
        :src="photoSrc"
        @error="imageError"
        @load="onLoad"
      />
      <div class="sr-only">Student profile page</div>
    </a>
  </div>
</template>

<script setup>
import {computed, ref} from 'vue'
import photoPlaceholder from '@/assets/images/roster_photo_placeholder.svg'
import photoUnavailable from '@/assets/images/photo_unavailable.svg'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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
})

const contextStore = useContextStore()
const imageErrored = ref(false)

const photoSrc = computed(() => {
  if (imageErrored.value) {
    return photoUnavailable
  } else {
    return props.photoUrl
  }
})

const imageError = () => {
  props.onLoad()
  imageErrored.value = true
}
</script>

<style scoped>
.photo {
  height: 6rem;
  width: 4.5rem;
}
.photo-outer {
  display: flex;
  justify-content: center;
  margin-top: 5px;
}
@media print {
  .photo {
    height: 130px;
    width: 98px;
  }
  .photo-one-per-page {
    height: 400px;
    width: 300px;
  }
}
</style>
