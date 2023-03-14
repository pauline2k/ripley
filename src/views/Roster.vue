<template>
  <div v-if="!isLoading" class="page-roster">
    <v-container v-if="!error" fluid>
      <v-row align-v="start" class="page-roster print-hide roster-search pb-3" no-gutters>
        <v-col class="pb-2 pr-2" sm="3">
          <v-text-field
            id="roster-search"
            v-model="search"
            aria-label="Search people by name or SID"
            placeholder="Search People"
          />
        </v-col>
        <v-col class="pb-2" sm="3">
          <div v-if="sections">
            <v-select
              id="section-select"
              v-model="section"
              aria-label="Search specific section (defaults to all sections)"
              :options="sections"
            />
          </div>
        </v-col>
        <v-col cols="auto" sm="6">
          <div class="d-flex flex-wrap float-right">
            <div class="pr-2">
              <v-btn
                id="download-csv"
                class="text-light"
                :disabled="!students.length"
                variant="outlined"
                @click="downloadCsv"
              >
                <v-icon class="text-secondary" icon="download" /> Export<span class="sr-only"> CSV file</span>
              </v-btn>
            </div>
            <div>
              <v-btn
                id="print-roster"
                variant="outlined"
                @click="printRoster"
              >
                <v-icon icon="print" variant="primary" /> Print<span class="sr-only"> roster of students</span>
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col sm="12">
          <RosterPhotos v-if="students.length" :course-id="currentUser.canvasCourseId" :students="students" />
          <div v-if="!students.length">
            <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
            Students have not yet signed up for this class.
          </div>
        </v-col>
      </v-row>
    </v-container>
    <div v-if="!error">
      <v-progress-circular
        color="primary"
        indeterminate
      />
      <div aria-live="polite" class="pt-5 text-center w-100" role="alert">
        Downloading rosters. This may take a minute for larger classes.
      </div>
    </div>
    {{ error }}
    <div v-if="error" role="alert">
      <v-icon icon="mdi-exclamation-triangle" class="icon-red" />
      You must be a teacher in this bCourses course to view official student rosters.
    </div>
    <div v-if="!error && roster && !sections" role="alert">
      <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
      There are no currently maintained official sections in this course site.
    </div>
    <div v-if="!error && roster && sections && !students" role="alert">
      <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
      Students have not yet signed up for this class.
    </div>
  </div>
</template>

<script>
import CanvasUtils from '@/mixins/CanvasUtils'
import Context from '@/mixins/Context'
import RosterPhotos from '@/components/bcourses/roster/RosterPhotos'
import Utils from '@/mixins/Utils'
import {getRoster, getRosterCsv} from '@/api/course'

export default {
  name: 'Roster',
  mixins: [CanvasUtils, Context, Utils],
  components: {RosterPhotos},
  data: () => ({
    error: undefined,
    roster: undefined,
    search: undefined,
    sections: [{title: 'All sections', value: null}],
    section: null
  }),
  computed: {
    canvasCourse() {
      return this.roster.canvasCourse
    },
    students() {
      let students = this.roster.students
      const phrase = this.idx(this.search)
      if (phrase) {
        students = this.$_.filter(this.roster.students, student => {
          const idxMatch = student.idx.includes(phrase)
          return idxMatch && (!this.section || this.$_.includes(student.section_ccns, this.section.toString()))
        })
        let alert = this.section ? `Showing the ${students.length} students of section ${this.section}` : 'Showing all students'
        if (phrase) {
          alert += ` with '${phrase}' in name.`
        }
        this.$announcer.polite(alert)
      }
      return students
    },
  },
  created() {
    getRoster(this.currentUser.canvasCourseId).then(data => {
      this.roster = data
      this.$_.each(data.sections, section => {
        this.sections.push({
          ...section,
          ...{
            title: section.name,
            value: section.sectionId
          }
        })
      })
      this.$_.each(this.students, s => s.idx = this.idx(`${s.first_name} ${s.last_name} ${s.student_id}`))
    }).finally(() => this.$ready('Roster'))
  },
  methods: {
    downloadCsv() {
      getRosterCsv(this.currentUser.canvasCourseId).then(() => {
        this.$announcer.polite(`${this.canvasCourse.name} CSV downloaded`)
      })
    },
    idx(value) {
      return value && this.$_.trim(value).replace(/[^\w\s]/gi, '').toLowerCase()
    },
    printRoster() {
      this.printPage(`${this.idx(this.canvasCourse.name).replace(/\s/g, '-')}_roster`)
    }
  }
}
</script>

<style scoped lang="scss">
button {
  height: 38px;
  width: 76px;
}
.page-roster {
  background: $color-white;
  overflow: hidden;
  padding: 20px;

  .roster-search {
    background: transparent;
    border: 0;
    border-bottom: 1px solid $color-very-light-grey;
    margin: 0 0 15px;
    overflow: hidden;
    padding: 7px 0 5px;
  }

  @media print {
    overflow: visible;
    padding: 0;
    .roster-search {
      display: none;
    }
  }
}
</style>
