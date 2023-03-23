<template>
  <div style="background-color: lightgray" class="ma-2 pa-5">
    Here is a sample
    <a href="https://ucberkeley.test.instructure.com/courses/1461531/external_tools/36940" target="_blank">Roster photos</a>
    view in Junction, the legacy platform.
  </div>
  <Alert :closable="false" :error-message="error" />
  <div v-if="!isLoading && roster" class="page-roster">
    <Alert :error-message="error" :success-message="success" />
    <v-container v-if="!error" fluid>
      <v-row align-v="center" class="page-roster roster-search">
        <v-col class="pr-2" sm="3">
          <v-text-field
            id="roster-search"
            v-model="search"
            aria-label="Search people by name or SID"
            hide-details
            placeholder="Search People"
            variant="outlined"
          />
        </v-col>
        <v-col sm="3">
          <div v-if="sections">
            <v-select
              id="section-select"
              v-model="section"
              aria-label="Search specific section (defaults to all sections)"
              hide-details
              :items="sections"
              variant="outlined"
            />
          </div>
        </v-col>
        <v-col class="pt-3" cols="auto" sm="6">
          <div class="d-flex flex-wrap float-right">
            <div class="pr-2">
              <v-btn
                id="download-csv"
                :disabled="!students.length"
                variant="outlined"
                @click="downloadCsv"
              >
                <v-icon class="pr-2" icon="mdi-download" />
                Export<span class="sr-only"> CSV file</span>
              </v-btn>
            </div>
            <div>
              <v-btn
                id="print-roster"
                color="primary"
                @click="printRoster"
              >
                <v-icon class="pr-2 text-white" icon="mdi-printer" />
                Print<span class="sr-only"> roster of students</span>
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row>
        <v-col sm="12">
          <RosterPhotos
            v-if="students.length"
            :course-id="currentUser.canvasSiteId"
            :students="students"
          />
          <div v-if="!roster.students.length">
            <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
            Students have not yet signed up for this class.
          </div>
          <div v-if="!students.length">
            <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
            No students found matching your query.
          </div>
        </v-col>
      </v-row>
    </v-container>
    <v-snackbar
      v-model="screamInSpace"
      class="mb-3"
      close-on-content-click
      timeout="5000"
      variant="elevated"
    >
      <v-img
        alt="In space, no one can hear you scream."
        src="@/assets/images/in-space-no-one-can-hear-you-scream.jpg"
        width="40vw"
      />
    </v-snackbar>
  </div>
</template>

<script>
import Alert from '@/components/utils/Alert'
import Context from '@/mixins/Context'
import RosterPhotos from '@/components/bcourses/roster/RosterPhotos'
import {getRoster, getRosterCsv} from '@/api/canvas-course'
import {printPage} from '@/utils'

export default {
  name: 'Roster',
  mixins: [Context],
  components: {Alert, RosterPhotos},
  data: () => ({
    error: undefined,
    roster: undefined,
    screamInSpace: false,
    search: undefined,
    section: '',
    sections: undefined,
    students: undefined,
    success: undefined
  }),
  watch: {
    search() {
      this.recalculateStudents()
      this.screamInSpace = this.idx(this.search) === 'in space no one can hear you scream'
    },
    section() {
      return this.recalculateStudents()
    }
  },
  created() {
    if (this.currentUser.isTeaching) {
      getRoster(this.currentUser.canvasSiteId).then(
        data => {
          this.roster = data
          this.students = this.roster.students
          if (data.sections.length) {
            this.sections = [{title: 'All sections', value: ''}]
            this.$_.each(data.sections, section => {
              this.sections.push({
                ...section,
                ...{
                  title: section.name,
                  value: section.id
                }
              })
            })
          }
          this.$_.each(this.students, s => s.idx = this.idx(`${s.firstName} ${s.lastName} ${s.id}`))
        },
        error => this.error = error
      ).finally(() => this.$ready('Roster'))
    } else {
      this.error = 'You must be a teacher in this bCourses course to view official student rosters.'
      this.$ready('Roster')
    }
  },
  methods: {
    downloadCsv() {
      getRosterCsv(this.currentUser.canvasSiteId).then(() => {
        this.$announcer.polite(`${this.roster.canvasSite.name} CSV downloaded`)
      })
    },
    recalculateStudents() {
      const normalizedPhrase = this.idx(this.search)
      if (normalizedPhrase || this.section) {
        this.students = this.$_.filter(this.roster.students, student => {
          let showStudent = !normalizedPhrase || student.idx.includes(normalizedPhrase)
          if (this.section) {
            showStudent = showStudent && this.$_.map(student.sections || [], 'id').includes(this.section)
          }
          return showStudent
        })
        this.$announcer.polite(`${this.students.length} student${this.students.length === 1 ? '' : 's'} shown.`)
      } else {
        this.students = this.roster.students
      }
    },
    idx(value) {
      return value && this.$_.trim(value).replace(/[^\w\s]/gi, '').toLowerCase()
    },
    printRoster() {
      printPage(`${this.idx(this.roster.canvasSite.name).replace(/\s/g, '-')}_roster`)
    }
  }
}
</script>

<style scoped lang="scss">
.page-roster {
  @media print {
    .roster-search {
      display: none;
    }
  }
}
</style>
