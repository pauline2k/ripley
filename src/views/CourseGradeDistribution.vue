<template>
  <div class="canvas-application pa-5">
    <div v-if="!isLoading">
      <h1 id="page-header" tabindex="-1">Grade Distribution</h1>
      <div v-if="$_.get(gradeDistribution, 'demographics')" class="container mb-4">
        <DemographicsChart
          :change-series-color="changeSeriesColor"
          :chart-defaults="chartDefaults"
          :grade-distribution="gradeDistribution.demographics"
        />
      </div>
      <div v-if="$_.get(gradeDistribution, 'enrollments')" class="container mb-4">
        <PriorEnrollmentChart
          :change-series-color="changeSeriesColor"
          :chart-defaults="chartDefaults"
          :grade-distribution="gradeDistribution.enrollments"
        />
      </div>
    </div>
  </div>
</template>

<script>
import DemographicsChart from '@/components/bcourses/analytics/DemographicsChart'
import Context from '@/mixins/Context'
import {getGradeDistribution} from '@/api/canvas-site'
import PriorEnrollmentChart from '@/components/bcourses/analytics/PriorEnrollmentChart'

export default {
  name: 'CourseGradeDistribution',
  components: {
    DemographicsChart,
    PriorEnrollmentChart
  },
  mixins: [Context],
  data: () => ({
    chartDefaults: {
      chart: {
        backgroundColor: 'transparent',
        type: 'column'
      },
      legend: {
        align: 'right',
        enabled: true,
        floating: true,
        labelFormat: '{name} Grades',
        layout: 'vertical',
        verticalAlign: 'top',
        y: 50
      },
      plotOptions: {
        series: {
          dataLabels: {
            enabled: true,
            format: '{y}%',
            style: {
              textOutline: 'none'
            }
          },
          groupPadding: .1
        }
      },
      series: [
        {
          data: []
        }
      ],
      title: false,
      tooltip: {
        format: '<div class="chart-tooltip-key">{key} Grade</div><div class="chart-tooltip-name">{series.name}</div><div class="chart-tooltip-value">{y}% of class</div>',
        stickOnContact: true,
        useHTML: true
      },
      xAxis: {
        categories: []
      },
      yAxis: {
        endOnTick: false,
        gridLineWidth: 0,
        labels: {
          format: '{value}%'
        },
        lineWidth: 1,
        tickWidth: 1,
        title: {
          enabled: false
        }
      }
    },
    gradeDistribution: undefined,
    colors: {
      default: '#8BBDDA',
      primary: '#CCCCCC',
      secondary: '#DAB38B'
    }
  }),
  created() {
    this.loadingStart()
    getGradeDistribution(this.currentUser.canvasSiteId).then(
      data => {
        this.gradeDistribution = data
        this.loadPrimarySeries()
      }
    ).finally(() => this.$ready('Grade Distribution'))
  },
  methods: {
    changeSeriesColor(chartSettings) {
      const primarySeries = chartSettings.series[0]
      const secondarySeries = this.$_.get(chartSettings.series, 1)
      const primarySeriesColor = secondarySeries ? this.colors.primary : this.colors.default
      primarySeries.color = primarySeriesColor
      chartSettings.colors[0] = primarySeriesColor
      this.$_.each(primarySeries.data, item => {
        item.color = primarySeriesColor
        item.dataLabels.color = item.y < 20 ? primarySeriesColor : 'white'
      })
      if (secondarySeries) {
        secondarySeries.color = this.colors.secondary
        this.$_.each(this.$_.get(secondarySeries, 'data', []), item => {
          item.color = this.colors.secondary
          item.dataLabels.color = item.y < 20 ? this.colors.secondary : 'white'
        })
      }
    },
    loadPrimarySeries() {
      this.chartDefaults.colors = [this.colors.default, this.colors.secondary]
      this.chartDefaults.series[0].name = 'Fall 2023'
      this.chartDefaults.series[0].color = this.colors.default
      this.$_.each(this.gradeDistribution.demographics, item => {
        this.chartDefaults.series[0].data.push({
          color: this.colors.default,
          dataLabels: {
            color: item.total < 20 ? this.colors.default : 'white',
            enabled: true,
            format: '{y}%',
            y: item.total < 20 ? 0 : 20
          },
          y: item.total
        })
        this.chartDefaults.xAxis.categories.push(item.grade)
      })
    }
  }
}
</script>

<style lang="scss">
.chart-tooltip-key {
  font-size: 13px;
  font-weight: bold;
}
.chart-tooltip-name {
  color: $color-grey-disabled;
  margin: 2px 0;
  text-transform: uppercase !important;
}
.chart-tooltip-value {
  font-size: 13px;
}
</style>
