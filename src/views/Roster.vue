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
      <v-row align-v="start" class="page-roster print-hide roster-search pb-3" no-gutters>
        <v-col class="pb-2 pr-2" sm="3">
          <v-text-field
            id="roster-search"
            v-model="search"
            aria-label="Search people by name or SID"
            placeholder="Search People"
            variant="outlined"
          />
        </v-col>
        <v-col class="pb-2" sm="3">
          <div v-if="sections">
            <v-select
              id="section-select"
              v-model="section"
              aria-label="Search specific section (defaults to all sections)"
              :items="sections"
              variant="outlined"
            >
              <template #selection="{ item }">
                {{ item.value }}
                <span v-if="!item.value">
                  All sections
                </span>
                <span
                  v-if="item.value"
                >
                  {{ item.title }}
                </span>
              </template>
            </v-select>
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
          <RosterPhotos v-if="students.length" :course-id="currentUser.canvasSiteId" :students="students" />
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
  </div>
</template>

<script>
import Alert from '@/components/utils/Alert'
import Context from '@/mixins/Context'
import RosterPhotos from '@/components/bcourses/roster/RosterPhotos'
import Utils from '@/mixins/Utils'
import {getRoster, getRosterCsv} from '@/api/canvas-course'

export default {
  name: 'Roster',
  mixins: [Context, Utils],
  components: {Alert, RosterPhotos},
  data: () => ({
    error: undefined,
    roster: undefined,
    search: undefined,
    section: undefined,
    sections: undefined,
    students: undefined,
    success: undefined
  }),
  watch: {
    search(rosterSearch) {
      const phrase = this.idx(rosterSearch)
      if (phrase) {
        this.students = []
        this.students = this.$_.filter(this.roster.students, student => {
          const idxMatch = student.idx.includes(phrase)
          return idxMatch && (!this.section || this.$_.includes(student.section_ccns, this.section.toString()))
        })
        this.$announcer.polite(`${this.students.length} student${this.students.length === 1 ? '' : 's'} shown.`)
      } else {
        this.students = this.roster.students
      }
    }
  },
  created() {
    if (this.currentUser.isTeaching) {
      getRoster(this.currentUser.canvasSiteId).then(
        data => {
          this.roster = data
          this.students = this.roster.students
          if (data.sections.length) {
            this.sections = [{title: 'All sections', value: null}]
            this.$_.each(data.sections, section => {
              this.sections.push({
                ...section,
                ...{
                  title: section.name,
                  value: section.ccn
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
    idx(value) {
      return value && this.$_.trim(value).replace(/[^\w\s]/gi, '').toLowerCase()
    },
    printRoster() {
      this.printPage(`${this.idx(this.roster.canvasSite.name).replace(/\s/g, '-')}_roster`)
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
