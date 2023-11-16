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
      <v-card v-if="size(get(gradeDistribution, 'demographics'))" class="container mb-4" elevation="0">
        <DemographicsChart
          :chart-defaults="chartDefaults"
          :colors="colors"
          :course-name="gradeDistribution.courseName"
          :grade-distribution="gradeDistribution.demographics"
        />
      </v-card>
      <v-card v-if="size(get(gradeDistribution, 'enrollments'))" class="container mb-4" elevation="0">
        <PriorEnrollmentChart
          :chart-defaults="chartDefaults"
          :colors="colors"
          :course-name="gradeDistribution.courseName"
          :grade-distribution="gradeDistribution.enrollments"
          :terms="orderBy(gradeDistribution.terms, ['id'], ['desc'])"
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
import {get, orderBy, size} from 'lodash'
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
      lang: {
        noData: 'No data available until final grades are returned.'
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
      noData: {
        style: {
          fontSize: '18px',
          color: '#999'
        }
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
    colors: {
      primary: '#8BBDDA',
      secondary: '#DAB38B',
      tertiary: '#C5E1F2'
    },
    errorMessage: undefined,
    gradeDistribution: undefined
  }),
  created() {
    this.loadingStart()
    this.chartDefaults.series[0].color = this.colors.primary
    getGradeDistribution(this.currentUser.canvasSiteId).then(
      data => {
        this.gradeDistribution = data
      },
      error => this.showError(error)
    ).catch(error => this.showError(error)
    ).finally(() => this.$ready())
  },
  methods: {
    get,
    orderBy,
    showError(errorMessage) {
      this.errorMessage = errorMessage
    },
    size
  }
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type  -->
<style lang="scss">
.grade-distribution {
  hr {
    border-color: $color-nobel !important;
    border-style: solid none none !important;
    color: $color-nobel !important;
  }
  table {
    caption {
      color: $color-body-black !important;
    }
    tbody tr:hover {
      background-color: $color-table-cell-bg-grey;
    }
  }
}
</style>
