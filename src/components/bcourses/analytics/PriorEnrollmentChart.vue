<template>
  <div class="pa-5">
    <div class="pl-3">
      <h2 id="grade-distribution-enrollment-header">Grade Distribution by Prior Enrollment</h2>
      <div>Lorem ipsum</div>
      <div class="grade-dist-enroll-course-search d-flex align-center my-4 pt-2">
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
      <hr aria-hidden="true" class="mb-3" />
    </div>
    <v-overlay
      v-model="isLoadingPriorEnrollments"
      class="align-center justify-center"
      contained
    >
      <PageLoadProgress v-if="isLoadingPriorEnrollments" color="primary" />
    </v-overlay>
    <highcharts :options="chartSettings"></highcharts>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import {cloneDeep, debounce, each, get, isEmpty, keys, max, size, toUpper} from 'lodash'
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
    this.chartSettings.plotOptions.series.lineWidth = 0
    this.chartSettings.plotOptions.series.dataLabels = {
      enabled: true
    }
    this.chartSettings.plotOptions.series.states = {
      hover: {
        lineWidthPlus: 0
      }
    }
    each(this.chartSettings.series[0].data, item => {
      item.dataLabels = this.getDataLabel(item.percentage, this.chartSettings.series[0].color)
    })
    this.chartSettings.title.text = `Overall Class Grade Distribution&mdash;${this.course.term.name}`
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
    this.loadPrimarySeries()
    this.debouncedSearch = debounce(this.search, 300)
  },
  methods: {
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
    loadPrimarySeries() {
      const color = this.chartSettings.series[0].color
      const courseName = this.gradeDistribution[0].courseName
      this.chartSettings.series[0].name = `${this.course.term.name} ${courseName}`
      each(this.gradeDistribution, item => {
        this.chartSettings.series[0].data.push({
          color: color,
          custom: {
            courseName: item.courseName,
            symbol: '\u25A0'
          },
          dataLabels: this.getDataLabel(item.y, color),
          y: item.percentage
        })
        this.chartSettings.xAxis.categories.push(item.grade)
      })
    },
    loadPriorEnrollments() {
      const marker = {
        enabled: true,
        lineWidth: 0
      }
      const gradesWithoutPriorEnroll = {
        color: this.colors.default,
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
      each(this.priorEnrollmentGradeDistribution[this.selectedTerm], item => {
        gradesWithoutPriorEnroll.data.push({
          custom: {
            courseName: item.courseName,
            symbol: '\u25C6'
          },
          dataLabels: {
            enabled: false
          },
          y: get(item, 'noPriorEnrollPercentage', 0)
        })
        gradesWithPriorEnroll.data.push({
          custom: {
            courseName: item.courseName,
            symbol: '\u25CF'
          },
          dataLabels: {
            enabled: false
          },
          y: get(item, 'priorEnrollPercentage', 0)
        })
      })
      this.chartSettings.series[1] = gradesWithoutPriorEnroll
      this.chartSettings.series[2] = gradesWithPriorEnroll
      this.chartSettings.series[0].color = this.colors.primary
      each(this.chartSettings.series[0].data, item => {
        item.color = this.colors.primary
        item.dataLabels = this.getDataLabel(item.y, this.colors.primary)
      })
      this.chartSettings.title.text =`Relation of ${this.gradeDistribution[0].courseName} Students Who Have and Have Not Taken ${this.selectedCourse}&mdash;${this.course.term.name}`
    },
    onClickAddCourse() {
      if (this.selectedCourse) {
        this.isLoadingPriorEnrollments = true
        getPriorEnrollmentGradeDistribution(this.currentUser.canvasSiteId, this.selectedCourse).then(response => {
          this.courseSearchText = null
          this.priorEnrollmentGradeDistribution = response
          this.selectedTerm = max(keys(response))
          this.loadPriorEnrollments()
          this.isLoadingPriorEnrollments = false
        })
      }
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
</style>
