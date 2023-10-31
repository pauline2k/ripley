<template>
  <div class="pa-5">
    <h2 id="grade-distribution-enrollment-header">Grade Distribution by Prior Enrollment</h2>
    <div>Lorem ipsum</div>
    <select
      id="grade-distribution-enrollment-select"
      v-model="selectedCourse"
      class="my-4"
      @change="onSelectCourse"
    >
      <option :value="null">Select Prior Enrollment</option>
      <option
        v-for="(option, index) in courses"
        :id="`grade-distribution-enrollment-option-${index}`"
        :key="index"
        :value="option"
      >
        {{ option }}
      </option>
    </select>
    <highcharts :options="chartSettings"></highcharts>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import {cloneDeep, each, get, keys} from 'lodash'

export default {
  name: 'PriorEnrollmentChart',
  components: {
    highcharts: Chart
  },
  mixins: [Context],
  props: {
    changeSeriesColor: {
      required: true,
      type: Function
    },
    chartDefaults: {
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
    courses: [],
    selectedCourse: null
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
    this.courses = keys(this.gradeDistribution)
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
    onSelectCourse() {
      if (this.selectedCourse) {
        const gradesWithoutPriorEnroll = {
          data: [],
          name: `Have not taken ${this.selectedCourse}`
        }
        const gradesWithPriorEnroll = {
          data: [],
          name: `Have taken ${this.selectedCourse}`
        }
        each(this.gradeDistribution[this.selectedCourse], item => {
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
        this.chartSettings.series[0].type = 'spline'
        this.chartSettings.series[1] = gradesWithoutPriorEnroll
        this.chartSettings.series[2] = gradesWithPriorEnroll
      } else if (this.chartSettings.series.length > 1) {
        this.chartSettings.series.splice(1, 2)
        this.chartSettings.series[0].type = 'column'
      }
      this.changeSeriesColor(this.chartSettings)
      each(this.chartSettings.series[0].data, item => {
        item.dataLabels = this.getDataLabel(item.y, this.chartSettings.series[0].color)
      })
    }
  }
}
</script>
