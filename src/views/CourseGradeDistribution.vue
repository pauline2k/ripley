<template>
  <div class="pa-5">
    <div v-if="!isLoading">
      <Header1 text="Grade Distribution" />
      <v-alert
        v-if="errorMessage"
        role="alert"
        :text="errorMessage"
        type="warning"
      />
      <div v-if="get(gradeDistribution, 'demographics')" class="container mb-4">
        <DemographicsChart
          :change-series-color="changeSeriesColor"
          :chart-defaults="chartDefaults"
          :grade-distribution="gradeDistribution.demographics"
        />
      </div>
      <div v-if="get(gradeDistribution, 'enrollments')" class="container mb-4">
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
import Context from '@/mixins/Context'
import DemographicsChart from '@/components/bcourses/analytics/DemographicsChart'
import Header1 from '@/components/utils/Header1.vue'
import PriorEnrollmentChart from '@/components/bcourses/analytics/PriorEnrollmentChart'
import {each, get} from 'lodash'
import {getGradeDistribution} from '@/api/canvas-site'

export default {
  name: 'CourseGradeDistribution',
  components: {
    DemographicsChart,
    Header1,
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
        verticalAlign: 'top'
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
        formatter: function () {
          const header = `<div class="chart-tooltip-key">${this.x} Grade</div>`
          return (this.points || []).reduce((tooltipText, point, index) => {
            return `${tooltipText}${index === 1 ? '<hr class="my-2"/>' : ''}
              <div class="chart-tooltip-series">
                <div class="chart-tooltip-name"><span style="color:${point.color}">\u25CF</span>${point.series.name}</div>
                <div class="chart-tooltip-value">Ratio of Class: <span class="font-weight-bold">${point.y}%</span></div>
                <div class="chart-tooltip-value">Student Count: <span class="font-weight-bold">${point.point.custom.count}</span></div>
              </div>`
          }, header)

        },
        shared: true,
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
      },
      error => this.showError(error)
    ).catch(error => this.showError(error)
    ).finally(() => this.$ready())
  },
  methods: {
    changeSeriesColor(chartSettings) {
      const defaultSeries = chartSettings.series[0]
      const primarySeries = get(chartSettings.series, 1)
      const secondarySeries = get(chartSettings.series, 2)
      const defaultSeriesColor = (primarySeries && !secondarySeries) ? this.colors.primary : this.colors.default
      defaultSeries.color = defaultSeriesColor
      chartSettings.colors[0] = defaultSeriesColor
      each(defaultSeries.data, item => {
        item.color = defaultSeriesColor
        item.dataLabels = this.getDataLabel(item.y, defaultSeriesColor)
        item.dataLabels.enabled = !primarySeries
      })
      if (primarySeries) {
        const primarySeriesColor = secondarySeries ? this.colors.primary : this.colors.secondary
        primarySeries.color = primarySeriesColor
        each(get(primarySeries, 'data', []), item => {
          item.color = primarySeriesColor
        })
      }
      if (secondarySeries) {
        secondarySeries.color = this.colors.secondary
        each(get(secondarySeries, 'data', []), item => {
          item.color = this.colors.secondary
        })
      }
    },
    get,
    getDataLabel(yVal, color) {
      const displayAboveColumn = yVal < 2
      return {
        color: displayAboveColumn ? color : 'white',
        enabled: true,
        format: '{y}%',
        y: displayAboveColumn ? 2 : 22
      }
    },
    loadPrimarySeries() {
      this.chartDefaults.colors = [this.colors.default, this.colors.secondary]
      this.chartDefaults.series[0].name = 'Fall 2023'
      this.chartDefaults.series[0].color = this.colors.default
      each(this.gradeDistribution.demographics, item => {
        this.chartDefaults.series[0].data.push({
          color: this.colors.default,
          custom: {count: item.count},
          dataLabels: this.getDataLabel(item.percentage, this.colors.default),
          y: item.percentage
        })
        this.chartDefaults.xAxis.categories.push(item.grade)
      })
    },
    showError(errorMessage) {
      this.errorMessage = errorMessage
    }
  }
}
</script>

<style scoped lang="scss">
/* eslint-disable vue-scoped-css/no-unused-selector */
.chart-tooltip-key {
  font-size: 15px;
  font-weight: bold;
  padding: 0 4px
}
.chart-tooltip-name {
  align-items: center;
  color: $color-grey-disabled;
  display: flex;
  font-size: 13px;
  font-weight: bold;
  height: 10px;
  margin: 4px 0;
  text-transform: uppercase !important;
  span {
    font-size: 24px;
    padding-right: 2px;
  }
}
.chart-tooltip-series {
  padding: 2px 4px 4px;
}
.chart-tooltip-value {
  font-size: 14px;
}
/* eslint-enable vue-scoped-css/no-unused-selector */
</style>
