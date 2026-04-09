<template>
  <ul aria-labelledby="page-title" class="pa-0 photo-list text-center">
    <li
      v-for="student in students"
      :key="student.studentId"
      class="photo-wrapper"
      :class="showOnePhotoPerPage ? 'photo-wrapper-one-per-page' : ''"
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
          <div v-if="student.email">
            <div class="page-roster-student-name text-medium-emphasis mt-2">
              <OutboundLink :id="`student-email-${student.studentId}`" :href="`mailto:${student.email}`" hide-icon>
                <span class="sr-only">Email </span>
                <span class="font-weight-regular">{{ student.firstName }}</span>
                <br>
                <span class="sr-only">&NonBreakingSpace;</span>
                {{ student.lastName }}
                <v-icon class="photo-email-icon" :icon="mdiEmailOutline" size="x-small" />
              </OutboundLink>
            </div>
          </div>
        </v-card-title>
        <v-card-text>
          <div :id="`student-id-${student.studentId}`" class="display-none-when-print">
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
.page-roster-student-name text-medium-emphasis {
  display: block;
  line-height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.photo-list {
  display: block;
  margin-left: 1rem;
  padding-top: 1rem;
  width: 100%;
}
.photo-wrapper {
  float: left;
  padding: 0 5px 5px;
  width: 173px;
}

@media print {
  a {
    text-decoration: none;
  }
  a[href]::after {
    content: none;
  }
  .page-roster-student-name text-medium-emphasis {
    font-size: 14px;
    line-height: 20px;
    text-overflow: ellipsis;
  }
  *.v-card-roster-photo {
    margin: 0 !important;
  }
  .photo-list {
    display: table;
  }
  .photo-email-icon {
    display: none;
  }
  .photo-wrapper {
    padding: 0;
    width: 150px;
  }
  .photo-wrapper-one-per-page {
    display: block;
    float: none;
    page-break-after: always;
    width: 300px;
  }
  .photo-wrapper-one-per-page:last-child {
    page-break-after: avoid;
  }
}

</style>
