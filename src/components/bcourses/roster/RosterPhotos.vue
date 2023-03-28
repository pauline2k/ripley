<template>
  <div class="d-flex flex-wrap text-center">
    <v-card
      v-for="student in students"
      :key="student.id"
      :border="false"
      elevation="0"
      class="mb-2 text-center"
      width="150"
    >
      <a
        :id="`student-profile-url-${student.id}`"
        class="text-decoration-none"
        :href="student.profileUrl || `/redirect/canvas/${canvasSiteId}/user/${student.canvasUserId}`"
        target="_top"
      >
        <RosterPhoto :student="student" />
      </a>
      <v-card-title class="py-0 text-subtitle-2">
        <div v-if="!student.email" :id="`student-without-email-${student.id}`">
          <div class="page-roster-student-name">{{ student.firstName }}</div>
          <div class="page-roster-student-name font-weight-bolder">{{ student.lastName }}</div>
        </div>
        <div v-if="student.email" class="pt-2">
          <OutboundLink :id="`student-email-${student.id}`" :href="`mailto:${student.email}`">
            <div class="sr-only">Email</div>
            <div class="page-roster-student-name">{{ student.firstName }}</div>
            <div class="page-roster-student-name font-weight-bolder">{{ student.lastName }}</div>
          </OutboundLink>
        </div>
      </v-card-title>
      <v-card-text>
        <div :id="`student-id-${student.id}`" class="print-hide">
          <span class="sr-only">Student ID: </span>
          {{ student.id }}
        </div>
        <div
          v-if="student.terms_in_attendance"
          :id="`student-terms-in-attendance-${student.id}`"
          class="page-roster-student-terms print-hide"
        >
          Terms: {{ student.terms_in_attendance }}
        </div>
        <div
          v-if="student.majors"
          :id="`student-majors-${student.id}`"
          class="page-roster-student-majors print-hide"
        >
          {{ $_.truncate(student.majors.join(', '), {length: 50}) }}
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import OutboundLink from '@/components/utils/OutboundLink'
import RosterPhoto from '@/components/bcourses/roster/RosterPhoto'

export default {
  name: 'RosterPhotos',
  components: {OutboundLink, RosterPhoto},
  props: {
    canvasSiteId: {
      required: true,
      type: Number
    },
    students: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    context: 'canvas'
  })
}
</script>

<style scoped lang="scss">
.page-roster-student-name {
  display: block;
  line-height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-roster-photos-list {
  display: block;
  overflow: hidden;
  width: 100%;
  li {
    display: block;
    float: left;
    height: auto;
  }
}

@media print {
  a[href]::after {
    content: none;
  }

  .page-roster-student-name {
    font-size: 18px;
    overflow: visible;
    text-overflow: ellipsis;
    white-space: normal;
  }

  .page-roster-photos-list {
    li {
      height: auto;
      margin-top: 15px;
      page-break-inside: avoid;
      width: 220px;
    }
  }
}
</style>
