<template>
  <div class="canvas-application pa-5">
    <div v-if="!isLoading">
      <h1 id="page-header" tabindex="-1">Grade Distribution</h1>
      <div class="container">
        <h2 class="ml-2">Grade Distribution by Demographics</h2>
        <div class="ml-2">Lorem ipsum</div>
        <select
          id="grade-distribution-select"
          v-model="selectedDemographic"
          class="ma-4 ml-2"
          @change="onSelectDemographic"
        >
          <option value="">Select Demographic</option>
          <optgroup
            v-for="(options, group) in demographicOptions"
            :key="group"
            :label="optionGroupLabels[group]"
          >
            <option
              v-for="(option, index) in options"
              :key="index"
              :value="{'group': group, 'option': option}"
            >
              {{ option }}
            </option>
          </optgroup>
        </select>
        <highcharts :options="chartOptions"></highcharts>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import {getGradeDistribution} from '@/api/canvas-site'

export default {
  name: 'CourseGradeDistribution',
  components: {
    highcharts: Chart
  },
  mixins: [Context],
  data: () => ({
    chartOptions: {
      chart: {
        type: 'column'
      },
      legend: {
        align: 'right',
        enabled: true,
        floating: true,
        layout: 'vertical',
        squareSymbol: true,
        verticalAlign: 'top',
        y: 50
      },
      plotOptions: {
        series: {
          groupPadding: .1
        }
      },
      series: [
        {
          data: []
        }
      ],
      xAxis: {
        categories: []
      },
      yAxis: {
        endOnTick: false,
        gridLineWidth: 0,
        lineWidth: 1,
        tickWidth: 1
      }
    },
    demographicOptions: {},
    optionGroupLabels: {
      ethnicities: 'Ethnicity',
      genders: 'Gender',
      transferStatus: 'Transfer Student',
      underrepresentedMinorityStatus: 'Underrepresented Minority',
      visaTypes: 'VISA Type'
    },
    rawData: undefined,
    selectedDemographic: undefined
  }),
  created() {
    this.loadingStart()
    this.selectedDemographic = ''
    getGradeDistribution(this.currentUser.canvasSiteId).then(
      data => {
        this.rawData = data.demographics
        this.$_.each(this.rawData, (item, key) => {
          this.chartOptions.series[0].name = 'Fall 2023 Grades'
          this.chartOptions.series[0].data.push({
            dataLabels: {
              enabled: true,
              y: 20
            },
            y: item.total
          })
          this.chartOptions.xAxis.categories.push(key)
          this.$_.each(item, (values, category) => {
            if (category in this.demographicOptions) {
              this.demographicOptions[category] = this.$_.union(this.demographicOptions[category], this.$_.keys(values))
            } else {
              this.demographicOptions[category] = this.$_.keys(values)
            }
          })
        })
      }
    ).finally(() => this.$ready('Grade Distribution'))
  },
  methods: {
    onSelectDemographic() {
      const group = this.$_.get(this.selectedDemographic, 'group')
      const option = this.$_.get(this.selectedDemographic, 'option')
      const comparisonSeries = {
        name: `${this.optionGroupLabels[group]} &mdash; ${option} Grades`,
        data: []
      }
      this.$_.each(this.rawData, item => {
        comparisonSeries.data.push({
          dataLabels: {
            enabled: true,
            y: 20
          },
          y: item[group][option]
        })
      })
      this.chartOptions.series[1] = comparisonSeries

    }
  }
}
</script>
