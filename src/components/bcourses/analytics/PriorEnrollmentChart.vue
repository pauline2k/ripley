<template>
  <div class="pa-5">
    <h2 id="grade-distribution-enrollment-header">Grade Distribution by Prior Enrollment</h2>
    <div>Lorem ipsum</div>
    <v-autocomplete
      id="grade-distribution-enrollment-course-search"
      v-model="selectedCourse"
      auto-select-first
      density="compact"
      :error="!suppressValidation && !isEmpty(courseSearchErrors)"
      :error-messages="!suppressValidation ? courseSearchErrors : []"
      :hide-no-data="isSearching || !courseSearchText"
      :items="courseSuggestions"
      :loading="isSearching ? 'primary' : false"
      :search="courseSearchText"
      variant="outlined"
      @change="suppressValidation = false"
      @update:model-value="onSelectCourse"
      @update:search="debouncedSearch"
    />
    <highcharts :options="chartSettings"></highcharts>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import {cloneDeep, debounce, each, get, isEmpty, keys, max} from 'lodash'
import {getPriorEnrollmentGradeDistribution, searchCourses} from '@/api/grade-distribution'

export default {
  name: 'PriorEnrollmentChart',
  components: {
    highcharts: Chart
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
    courseSearchText: undefined,
    courseSuggestions: [],
    debouncedSearch: undefined,
    courseSearchErrors: [],
    isSearching: false,
    priorEnrollmentGradeDistribution: [],
    selectedCourse: undefined,
    selectedTerm: undefined,
    suppressValidation: true
  }),
  created() {
    this.chartSettings = cloneDeep(this.chartDefaults)
    this.chartSettings.chart.type = 'column'
    this.chartSettings.plotOptions.series.dataLabels = {
      enabled: true
    }
    each(this.chartSettings.series[0].data, item => {
      item.dataLabels = this.getDataLabel(item.percentage, this.chartSettings.series[0].color)
    })
    this.chartSettings.title = {
      align: 'left',
      text: `Overall Class Grade Distribution&mdash;${this.course.term.name}`
    }
    this.chartSettings.yAxis.labels = {
      format: '{value}%'
    }
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
      this.chartSettings.series[0].name = `${this.course.term.name} ${this.course.courseCode}`
      each(this.chartSettings.series[0].data, item => {
        item.dataLabels = this.getDataLabel(item.y, color)
      })
      each(this.gradeDistribution, item => {
        this.chartSettings.series[0].data.push({
          color: color,
          custom: {count: item.count},
          dataLabels: this.getDataLabel(item.y, color),
          y: item.percentage
        })
        this.chartSettings.xAxis.categories.push(item.grade)
      })
    },
    loadPriorEnrollments() {
      const gradesWithoutPriorEnroll = {
        color: this.colors.secondary,
        data: [],
        name: `Have not taken ${this.selectedCourse}`
      }
      const gradesWithPriorEnroll = {
        color: this.colors.primary,
        data: [],
        name: `Have taken ${this.selectedCourse}`
      }
      each(this.priorEnrollmentGradeDistribution[this.selectedTerm], item => {
        console.log(item)
        gradesWithoutPriorEnroll.data.push({
          custom: {
            count: get(item, 'noPriorEnrollCount', 0)
          },
          dataLabels: {
            enabled: false
          },
          y: get(item, 'noPriorEnrollPercentage', 0)
        })
        gradesWithPriorEnroll.data.push({
          custom: {
            count: get(item, 'priorEnrollCount', 0)
          },
          dataLabels: {
            enabled: false
          },
          y: get(item, 'priorEnrollPercentage', 0)
        })
      })
      this.chartSettings.series[1] = gradesWithoutPriorEnroll
      this.chartSettings.series[2] = gradesWithPriorEnroll
      each(this.chartSettings.series[0].data, item => {
        item.dataLabels = this.getDataLabel(item.y, this.chartSettings.series[0].color)
      })
    },
    onSelectCourse() {
      if (this.selectedCourse) {
        getPriorEnrollmentGradeDistribution(this.currentUser.canvasSiteId, this.selectedCourse).then(response => {
          this.priorEnrollmentGradeDistribution = response
          this.selectedTerm = max(keys(response))
          this.loadPriorEnrollments()
        })
      } else if (this.chartSettings.series.length > 1) {
        this.chartSettings.series.splice(1, 2)
      }
    },
    search(text) {
      this.courseSearchText = text
      if (this.courseSearchText) {
        this.isSearching = true
        searchCourses(this.courseSearchText).then(response => {
          this.courseSuggestions = response.results
          this.isSearching = false
        })
      } else {
        this.courseSuggestions = []
      }
    }
  }
}
</script>
