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
    this.chartSettings = this.$_.cloneDeep(this.chartDefaults)
    this.courses = this.$_.keys(this.gradeDistribution)
  },
  methods: {
    onSelectCourse() {
      if (this.selectedCourse) {
        const gradesWithPriorEnroll = {
          data: [],
          name: this.selectedCourse
        }
        this.$_.each(this.gradeDistribution[this.selectedCourse], item => {
          gradesWithPriorEnroll.data.push({
            custom: {
              count: this.$_.get(item, 'priorEnrollCount', 0)
            },
            dataLabels: {
              enabled: false
            },
            y: this.$_.get(item, 'priorEnrollPercentage', 0)
          })
        })
        this.chartSettings.series[1] = gradesWithPriorEnroll
      } else if (this.chartSettings.series.length > 1) {
        this.chartSettings.series = [this.chartSettings.series[0]]
      }
      this.changeSeriesColor(this.chartSettings)
    }
  }
}
</script>
