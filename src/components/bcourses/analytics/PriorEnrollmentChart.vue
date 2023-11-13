<template>
  <div class="pa-5">
    <div class="pl-3">
      <h2 id="grade-distribution-enrollment-header">Grade Distribution by Prior Enrollment</h2>
      <div>Lorem ipsum</div>
      <div class="d-flex justify-space-between my-4 pt-2">
        <div class="grade-dist-enroll-course-search d-flex align-center">
          <v-autocomplete
            id="grade-distribution-enrollment-course-search"
            v-model="selectedCourse"
            auto-select-first
            bg-color="white"
            class="text-upper mr-2"
            density="compact"
            :disabled="isLoadingPriorEnrollments"
            :error="!suppressValidation && !isEmpty(courseSearchErrors)"
            :error-messages="!suppressValidation ? courseSearchErrors : []"
            hide-details
            hide-no-data
            :items="courseSuggestions"
            label="Search Classes..."
            :loading="isSearching ? 'primary' : false"
            :menu-icon="null"
            :search="courseSearchText"
            variant="outlined"
            @blur="selectedCourse = toUpper(courseSearchText)"
            @change="suppressValidation = false"
            @update:search="text => courseSearchText = text"
          >
            <template #item="{props, item}">
              <v-list-item
                v-bind="props"
                class="py-0 my-0"
                density="compact"
                height="unset"
                min-height="30"
                :title="item.raw"
                :value="item.raw"
              ></v-list-item>
            </template>
          </v-autocomplete>
          <v-btn
            id="grade-distribution-enroll-add-class-btn"
            class="font-size-13"
            color="primary"
            :disabled="!selectedCourse || isLoadingPriorEnrollments"
            @click="onClickAddCourse"
          >
            Add Class
          </v-btn>
        </div>
        <div class="position-relative">
          <select
            v-if="size(terms)"
            :value="get(selectedTerm, 'id')"
            class="position-absolute grade-dist-enroll-term-select"
            @change="onSelectTerm"
          >
            <option
              v-for="(term, index) in terms"
              :key="index"
              :value="term.id"
            >
              {{ term.name }}
            </option>
          </select>
        </div>
      </div>
      <hr aria-hidden="true" class="mb-3" />
    </div>
    <v-overlay
      v-model="isLoadingPriorEnrollments"
      class="align-center justify-center"
      contained
      persistent
    >
      <PageLoadProgress v-if="isLoadingPriorEnrollments" color="primary" />
    </v-overlay>
    <highcharts :options="chartSettings"></highcharts>
    <v-row v-if="selectedTerm" class="d-flex justify-center">
      <v-btn
        id="grade-distribution-enrollments-show-btn"
        aria-controls="page-help-notice"
        :aria-expanded="showTable"
        aria-haspopup="true"
        class="font-weight-medium text-no-wrap my-2"
        color="primary"
        :prepend-icon="showTable ? mdiArrowUpCircle : mdiArrowDownCircle"
        size="large"
        variant="text"
        @click="showTable = !showTable"
      >
        {{ showTable ? 'Hide' : 'Show' }} Data Table
      </v-btn>
    </v-row>
    <v-row v-if="selectedTerm" class="d-flex justify-center">
      <v-expand-transition>
        <v-card v-show="showTable" class="pb-2" width="700">
          <table id="grade-distribution-enroll-table" class="border-0 border-t">
            <caption class="font-weight-bold font-size-16 py-3" v-html="chartSettings.title.text"></caption>
            <thead class="bg-grey-lighten-4">
              <tr>
                <th class="font-weight-bold pl-4 py-2" scope="col">Grade</th>
                <th
                  v-for="(series, index) in chartSettings.series"
                  :key="index"
                  class="font-weight-bold py-2"
                  scope="col"
                >
                  {{ series.name }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(grade, gradeIndex) in chartSettings.xAxis.categories"
                :id="`grade-distribution-enroll-table-row-${gradeIndex}`"
                :key="gradeIndex"
              >
                <td :id="`grade-distro-enroll-table-row-${gradeIndex}-col-0`" class="pl-4 py-1">{{ grade }}</td>
                <td
                  v-for="(series, index) in chartSettings.series"
                  :id="`grade-distro-enroll-table-row-${gradeIndex}-col-${index + 1}`"
                  :key="index"
                  class="py-1"
                >
                  {{ series['data'][gradeIndex].y }}%
                </td>
              </tr>
            </tbody>
          </table>
        </v-card>
      </v-expand-transition>
    </v-row>
  </div>
</template>

<script setup>
import {mdiArrowDownCircle, mdiArrowUpCircle} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import {cloneDeep, debounce, each, find, get, includes, isEmpty, size, toUpper} from 'lodash'
import {getPriorEnrollmentGradeDistribution, searchCourses} from '@/api/grade-distribution'
import PageLoadProgress from '@/components/utils/PageLoadProgress.vue'

export default {
  name: 'PriorEnrollmentChart',
  components: {
    highcharts: Chart,
    PageLoadProgress
  },
  mixins: [Context],
  props: {
    chartDefaults: {
      required: true,
      type: Object
    },
    colors: {
      required: true,
      type: Object
    },
    course: {
      required: true,
      type: Object
    },
    gradeDistribution: {
      required: true,
      type: Object
    },
    terms: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    chartSettings: {},
    pendingCourseSearch: undefined,
    courseSearchText: undefined,
    courseSuggestions: [],
    debouncedSearch: undefined,
    courseSearchErrors: [],
    isLoadingPriorEnrollments: false,
    isSearching: false,
    priorEnrollmentGradeDistribution: {},
    selectedCourse: undefined,
    selectedTerm: undefined,
    showTable: false,
    suppressValidation: true
  }),
  watch: {
    courseSearchText(newVal, oldVal) {
      if (newVal) {
        if (newVal !== oldVal) {
          this.debouncedSearch()
        }
      }
    }
  },
  created() {
    this.chartSettings = cloneDeep(this.chartDefaults)
    this.chartSettings.chart.type = 'column'
    this.chartSettings.legend.labelFormat = '{name} grades'
    this.chartSettings.legend.symbolHeight = 12
    this.chartSettings.plotOptions.series.lineWidth = 0
    this.chartSettings.plotOptions.series.states = {
      hover: {
        lineWidthPlus: 0
      }
    }
    this.selectedTerm = get(this.terms, 0)
    this.chartSettings.title.widthAdjust = -200
    this.chartSettings.tooltip.distance = 24
    this.chartSettings.tooltip.formatter = function () {
      const header = `<div id="grade-dist-enroll-tooltip-grade" class="font-weight-bold font-size-15">${this.x} Grade</div>
          <div id="grade-dist-enroll-tooltip-course" class="font-size-13 text-grey-darken-1">${this.point.custom.courseName}</div>
          <div class="font-size-13 mb-2">
            Ratio of class: <span id="grade-dist-enroll-tooltip-series-0-value" class="font-weight-bold">${this.point.y}%</span>
          </div>
          <hr aria-hidden="true" class="mb-2 ${size(this.points) <= 1 ? 'd-none' : ''}" />`
      return (this.points.slice(1) || []).reduce((tooltipText, plot, index) => {
        return`${tooltipText}<div id="grade-dist-enroll-tooltip-series-${index + 1}" class="font-size-13 pb-2">
          <div class="text-grey-darken-1 text-uppercase">
            <span aria-hidden="true" class="grade-dist-enroll-tooltip-symbol" style="color:${plot.color}">${plot.point.custom.symbol}</span>
            ${plot.series.name}
          </div
          <div>
            Ratio of class: <span id="grade-dist-enroll-tooltip-series-${index + 1}-value" class="font-weight-bold">${plot.y}%</span>
          </div>
        </div>`
      }, header)
    }
    this.chartSettings.yAxis.labels.format = '{value}%'
    this.debouncedSearch = debounce(this.search, 300)
    this.loadPrimarySeries(this.colors.primary)
    this.setChartTitle()
  },
  methods: {
    get,
    getDataLabel(yVal, color) {
      if (this.chartSettings.series.length === 1) {
        const displayAboveColumn = yVal < 2
        return {
          color: displayAboveColumn ? color : 'white',
          enabled: true,
          format: '{y}%',
          style: {
            textOutline: 'none'
          },
          y: displayAboveColumn ? 2 : 22
        }
      } else {
        return {
          enabled: false
        }
      }
    },
    isEmpty,
    loadPrimarySeries(color, showLabels=true) {
      const courseName = this.gradeDistribution[this.selectedTerm.id][0].courseName
      this.chartSettings.series[0] = {
        color: color,
        name: `${this.selectedTerm.name} ${courseName}`,
        data: []
      }
      this.chartSettings.xAxis.categories = []
      each(this.gradeDistribution[this.selectedTerm.id], item => {
        this.chartSettings.series[0].data.push({
          color: color,
          custom: {
            courseName: item.courseName,
            symbol: '\u25A0'
          },
          dataLabels: showLabels ? this.getDataLabel(item.y, color) : {enabled: false},
          y: item.percentage
        })
        this.chartSettings.xAxis.categories.push(item.grade)
      })
      this.chartSettings.plotOptions.series.dataLabels = {
        enabled: showLabels
      }
    },
    loadPriorEnrollments() {
      const marker = {
        enabled: true,
        lineWidth: 0
      }
      const gradesWithoutPriorEnroll = {
        color: this.colors.primary,
        data: [],
        marker: {...marker, radius: 6, symbol: 'diamond'},
        name: `Have not taken ${this.selectedCourse}`,
        type: 'line'
      }
      const gradesWithPriorEnroll = {
        color: this.colors.secondary,
        data: [],
        marker: {...marker, radius: 5, symbol: 'circle'},
        name: `Have taken ${this.selectedCourse}`,
        type: 'line'
      }
      each(this.priorEnrollmentGradeDistribution[this.selectedTerm.id], item => {
        if (includes(this.chartSettings.xAxis.categories, item.grade )) {
          gradesWithoutPriorEnroll.data.push({
            custom: {
              courseName: item.courseName,
              symbol: '\u25C6'
            },
            dataLabels: {enabled: false},
            y: get(item, 'noPriorEnrollPercentage', 0)
          })
          gradesWithPriorEnroll.data.push({
            custom: {
              courseName: item.courseName,
              symbol: '\u25CF'
            },
            dataLabels: {enabled: false},
            y: get(item, 'priorEnrollPercentage', 0)
          })
        }
      })
      this.chartSettings.series[1] = gradesWithoutPriorEnroll
      this.chartSettings.series[2] = gradesWithPriorEnroll
    },
    onClickAddCourse() {
      if (this.selectedCourse) {
        this.isLoadingPriorEnrollments = true
        getPriorEnrollmentGradeDistribution(this.currentUser.canvasSiteId, this.selectedCourse).then(response => {
          this.courseSearchText = null
          this.priorEnrollmentGradeDistribution = response
          this.refresh()
          this.isLoadingPriorEnrollments = false
        })
      }
    },
    onSelectTerm(e) {
      const termId = e.target.value
      this.selectedTerm = find(this.terms, {'id': termId})
      this.refresh()
    },
    refresh() {
      if (get(this.priorEnrollmentGradeDistribution, this.selectedTerm.id)) {
        this.loadPrimarySeries(this.colors.tertiary, false)
        this.loadPriorEnrollments()
      } else {
        this.chartSettings.series = []
        this.loadPrimarySeries(this.colors.primary)
      }
      this.setChartTitle()
    },
    search() {
      this.isSearching = true
      if (this.pendingCourseSearch) {
        this.pendingCourseSearch.abort()
      }
      this.pendingCourseSearch = new AbortController()
      searchCourses(toUpper(this.courseSearchText), this.pendingCourseSearch).then(response => {
        this.courseSuggestions = response.results
        this.isSearching = false
      }).catch(() => {
        this.$nextTick(() => this.isSearching = false)
      })
    },
    setChartTitle() {
      if (size(this.chartSettings.series) === 3) {
        const courseName = this.gradeDistribution[this.selectedTerm.id][0].courseName
        this.chartSettings.title.text = `Relation of ${courseName} Students Who Have and Have Not Taken ${this.selectedCourse}&mdash;${this.selectedTerm.name}`
      } else {
        this.chartSettings.title.text = `Overall Class Grade Distribution&mdash;${this.selectedTerm.name}`
      }
    },
    size,
    toUpper
  }
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type  -->
<style lang="scss">
.grade-dist-enroll-tooltip-symbol {
  display: inline-block;
  font-size: 20px !important;
  line-height: 1.1px;
  position: relative;
  top: 1px;
  width: 16px;
}
.v-autocomplete.text-upper input {
  text-transform: uppercase !important;
}
</style>

<style lang="scss" scoped>
.grade-dist-enroll-course-search {
  width: 400px;
}
.grade-dist-enroll-term-select {
  right: 0;
  top: 75px;
  z-index: 100;
}
</style>
