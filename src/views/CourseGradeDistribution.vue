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
          :chart-defaults="chartDefaults"
          :colors="colors"
          :grade-distribution="gradeDistribution.demographics"
        />
      </div>
      <div v-if="get(gradeDistribution, 'enrollments')" class="container mb-4">
        <PriorEnrollmentChart
          :chart-defaults="chartDefaults"
          :colors="colors"
          :course="gradeDistribution.canvasSite"
          :grade-distribution="gradeDistribution.enrollments"
        />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DemographicsChart from '@/components/bcourses/analytics/DemographicsChart'
import Header1 from '@/components/utils/Header1'
import PriorEnrollmentChart from '@/components/bcourses/analytics/PriorEnrollmentChart'
import {each, get} from 'lodash'
import {getGradeDistribution} from '@/api/grade-distribution'

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
      },
      legend: {
        align: 'right',
        enabled: true,
        floating: true,
        labelFormat: '{name}',
        layout: 'vertical',
        squareSymbol: false,
        symbolHeight: 3,
        symbolRadius: 0,
        verticalAlign: 'top'
      },
      plotOptions: {
        series: {
          dataLabels: {
            enabled: false
          },
          groupPadding: .1,
          lineWidth: 3
        }
      },
      series: [
        {
          legendSymbol: 'rectangle',
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
        categories: [],
        labels: {
          autoRotationLimit: 0,
          overflow: 'allow',
          style: {
            color: '#999',
            fontSize: 15
          }
        },
        lineColor: '#CCC',
        lineWidth: 2,
        tickColor: '#CCC',
        tickmarkPlacement: 'on',
        tickWidth: 1
      },
      yAxis: {
        endOnTick: false,
        gridLineWidth: 0,
        labels: {
          style: {
            color: '#999',
            fontSize: 16
          }
        },
        lineColor: '#999',
        lineWidth: 1,
        tickColor: '#CCC',
        tickWidth: 1,
        title: {
          enabled: false
        }
      }
    },
    errorMessage: undefined,
    gradeDistribution: undefined,
    colors: {
      default: '#8BBDDA',
      primary: '#CCCCCC',
      secondary: '#DAB38B'
    }
  }),
  created() {
    this.loadingStart()
    this.chartDefaults.series[0].color = this.colors.default
    getGradeDistribution(this.currentUser.canvasSiteId).then(
      data => {
        this.gradeDistribution = data
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
