<template>
  <div>
    <div class="display-none-when-print">
      <v-alert
        v-if="error"
        class="ma-2"
        :closable="false"
        density="compact"
        role="alert"
        type="warning"
      >
        {{ error }}
      </v-alert>
    </div>
    <div v-if="!isLoading && roster">
      <v-alert
        v-if="success"
        class="ma-2"
        :closable="true"
        density="compact"
        role="alert"
        type="success"
      >
        {{ success }}
      </v-alert>
      <v-container v-if="!error" fluid>
        <v-row align-v="center" class="display-none-when-print">
          <v-col class="pr-2 roster-column-when-print" sm="3">
            <v-text-field
              id="roster-search"
              v-model="search"
              aria-label="Search people by name or SID"
              clearable
              hide-details
              placeholder="Search People"
              type="search"
              variant="outlined"
            />
          </v-col>
          <v-col sm="3">
            <div v-if="roster.sections">
              <select
                id="section-select"
                v-model="selectedSectionId"
                aria-label="Search specific section (defaults to all sections)"
                @change="onSelectSection"
              >
                <option :value="null">All Sections</option>
                <option
                  v-for="(section, index) in roster.sections"
                  :key="index"
                  :value="section.id"
                >
                  {{ section.name }}
                </option>
              </select>
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
                <v-tooltip
                  v-model="showPrintButtonTooltip"
                  location="top"
                  :text="printButtonTooltip"
                >
                  <template #activator="{props}">
                    <v-btn
                      id="print-roster"
                      color="primary"
                      :disabled="!students.length || disablePrintButton"
                      v-bind="props"
                      @click="printRoster"
                    >
                      <v-icon class="pr-2 text-white" icon="mdi-printer" />
                      Print<span class="sr-only"> roster of students</span>
                    </v-btn>
                  </template>
                </v-tooltip>
              </div>
            </div>
          </v-col>
        </v-row>
        <v-row>
          <v-col sm="12">
            <RosterPhotos
              v-if="students.length"
              :students="students"
            />
            <div v-if="!roster.students.length">
              <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
              Students have not yet signed up for this class.
            </div>
            <div v-if="roster.students.length && !students.length">
              <v-icon icon="mdi-exclamation-circle" class="icon-gold" />
              No students found matching your query.
            </div>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import RosterPhotos from '@/components/bcourses/roster/RosterPhotos'
import {exportRoster, getRoster} from '@/api/canvas-site'
import {printPage} from '@/utils'

export default {
  name: 'Roster',
  mixins: [Context],
  components: {RosterPhotos},
  data: () => ({
    error: undefined,
    printButtonTooltip: 'You can print when student images have loaded.',
    roster: undefined,
    search: undefined,
    selectedSectionId: null,
    showTooltip: true,
    students: undefined,
    success: undefined
  }),
  watch: {
    search() {
      this.recalculateStudents()
    }
  },
  computed: {
    disablePrintButton() {
      return !this.$_.size(this.students) || !!this.students.find(s => !s.hasRosterPhotoLoaded)
    },
    showPrintButtonTooltip: {
      get() {
        return !this.isLoading && this.showTooltip && this.disablePrintButton
      },
      set(value) {
        if (!value) {
          this.showTooltip = false
        }
      }
    }
  },
  created() {
    if (this.currentUser.isTeaching || this.currentUser.isAdmin) {
      getRoster(this.currentUser.canvasSiteId).then(
        data => {
          this.roster = data
          this.students = this.roster.students
          this.$_.each(this.students, s => s.idx = this.idx(`${s.firstName} ${s.lastName} ${s.studentId}`))
          // If student count is low then tooltip is not necessary.
          const threshold = 36
          this.showPrintButtonTooltip = (this.students.length >= threshold) && this.disablePrintButton
          this.$announcer.polite(this.printButtonTooltip)
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
      exportRoster(this.currentUser.canvasSiteId).then(() => {
        this.$announcer.polite(`${this.roster.canvasSiteName} CSV downloaded`)
      })
    },
    onSelectSection() {
      this.recalculateStudents()
    },
    recalculateStudents() {
      const normalizedPhrase = this.idx(this.search)
      if (normalizedPhrase || this.selectedSectionId) {
        this.students = this.$_.filter(this.roster.students, student => {
          let showStudent = !normalizedPhrase || student.idx.includes(normalizedPhrase)
          if (this.selectedSectionId) {
            showStudent = showStudent && this.$_.map(student.sections || [], 'id').includes(this.selectedSectionId)
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
      printPage(`${this.idx(this.currentUser.canvasSiteName).replace(/\s/g, '-')}_roster`)
    }
  }
}
</script>

<style scoped lang="scss">
@media print {
  .roster-column-when-print {
    padding: 0;
  }
}
</style>
