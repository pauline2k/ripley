<template>
  <div class="grade-distribution pa-5">
    <div v-if="!isLoading">
      <Header1 text="Grade Distribution" />
      <v-alert
        v-if="errorMessage"
        role="alert"
        :text="errorMessage"
        type="warning"
      />
      <v-card v-if="get(gradeDistribution, 'demographics')" class="container mb-4">
        <DemographicsChart
          :chart-defaults="chartDefaults"
          :colors="colors"
          :grade-distribution="gradeDistribution.demographics"
        />
      </v-card>
      <v-card v-if="get(gradeDistribution, 'enrollments')" class="container mb-4">
        <PriorEnrollmentChart
          :chart-defaults="chartDefaults"
          :colors="colors"
          :course="gradeDistribution.canvasSite"
          :grade-distribution="gradeDistribution.enrollments"
        />
      </v-card>
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
        itemStyle: {
          fontSize: '1em'
        },
        labelFormat: '{name}',
        layout: 'vertical',
        symbolPadding: 10,
        symbolRadius: 0,
        verticalAlign: 'top',
        y: 30
      },
      plotOptions: {
        series: {
          dataLabels: {
            enabled: false
          },
          groupPadding: .1
        }
      },
      series: [
        {
          data: []
        }
      ],
      title: {
        align: 'left',
        margin: 45,
        style: {
          color: '#474747'
        },
      },
      tooltip: {
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
      primary: '#C5E1F2',
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

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type  -->
<style lang="scss">
.grade-distribution hr {
  border-color: $color-nobel !important;
  border-style: solid none none !important;
  color: $color-nobel !important;
}
</style>
