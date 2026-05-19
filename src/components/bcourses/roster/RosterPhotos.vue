<template>
  <ul aria-labelledby="page-title" class="pa-0 photo-list text-center">
    <li
      v-for="student in students"
      :key="student.studentId"
      class="photo-wrapper"
      :class="{'photo-wrapper-one-per-page': showOnePhotoPerPage}"
    >
      <v-card
        :border="false"
        class="avoid-break-inside-when-print mb-2 text-center v-card-roster-photo"
        elevation="0"
      >
        <RosterPhoto
          :on-load="() => student.hasRosterPhotoLoaded = true"
          :photo-url="photoUrls[student.studentId]"
          :show-one-photo-per-page="showOnePhotoPerPage"
          :student="student"
        />
        <v-card-title class="py-0 text-subtitle-2">
          <div v-if="!student.email" :id="`student-without-email-${student.studentId}`">
            <div class="page-roster-student-name text-medium-emphasis font-weight-regular">{{ student.firstName }} </div>
            <div class="page-roster-student-name text-medium-emphasis">{{ student.lastName }}</div>
          </div>
          <div v-if="student.email" class="page-roster-student-name mt-2">
            <OutboundLink
              :id="`student-email-${student.studentId}`"
              :href="`mailto:${student.email}`"
              :icon="mdiEmailOutline"
            >
              <span class="sr-only">Email </span>
              <div class="font-weight-regular">{{ student.firstName }}</div>
              {{ student.lastName }}
            </OutboundLink>
          </div>
        </v-card-title>
        <v-card-text>
          <div :id="`student-id-${student.studentId}`" class="d-print-none">
            <span class="sr-only">Student ID: </span>
            {{ student.studentId }}
          </div>
          <div
            v-if="student.terms_in_attendance"
            :id="`student-terms-in-attendance-${student.studentId}`"
            class="page-roster-student-terms print-hide"
          >
            Terms: {{ student.terms_in_attendance }}
          </div>
          <div
            v-if="student.majors"
            :id="`student-majors-${student.studentId}`"
            class="page-roster-student-majors print-hide"
          >
            {{ truncate(student.majors.join(', '), {length: 50}) }}
          </div>
        </v-card-text>
      </v-card>
    </li>
  </ul>
</template>

<script setup>
import {each, trim, truncate} from 'lodash'
import {mdiEmailOutline} from '@mdi/js'
import {onMounted, ref} from 'vue'
import OutboundLink from '@/components/utils/OutboundLink'
import photoUnavailable from '@/assets/images/photo_unavailable.svg'
import RosterPhoto from '@/components/bcourses/roster/RosterPhoto'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  showOnePhotoPerPage: {
    required: true,
    type: Boolean
  },
  students: {
    required: true,
    type: Array
  }
})

const contextStore = useContextStore()
const photoUrls = ref({})

onMounted(() => {
  reloadPhotosDelayed()
})

const loadPhoto = student => {
  const photoUrl = trim(student.photoUrl || '')
  photoUrls.value[student.studentId] = photoUrl ? photoUrl.startsWith('http') ? photoUrl : `${contextStore.config.apiBaseUrl}${photoUrl}` : photoUnavailable
}

const reloadPhotosDelayed = () => {
  // Distribute photo loading requests with a slight delay so as not to bottleneck the browser.
  let interval = 0
  each(props.students, student => {
    setTimeout(() => loadPhoto(student), interval)
    interval = interval + 10
  })
}
</script>

<style scoped lang="scss">
.photo-list {
  display: flex;
  flex-wrap: wrap;
  margin-top: 1rem;
  width: 100%;
}
.photo-wrapper {
  padding: 5px;
  width: 11rem;
}

@media print {
  .page-roster-student-name {
    font-size: 14px;
    line-height: 20px;
    :deep(a), :deep(a .text-decoration-underline) {
      color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity)) !important;
      text-decoration: none !important;
    }
  }
  .photo-list {
    font-size: 100% !important;
  }
  .photo-wrapper {
    width: 150px;
  }
  .photo-wrapper-one-per-page {
    align-items: center;
    display: flex;
    float: none;
    height: 100vh;
    justify-content: center;
    page-break-after: always;
    width: 100%;
    .v-card-roster-photo {
      width: 300px;
    }
  }
  .photo-wrapper-one-per-page:last-child {
    page-break-after: avoid;
  }
  .v-card-roster-photo {
    margin: 0 !important;
  }
}
</style>
