<template>
  <div class="grade-distribution-demographics pa-5">
    <h2 id="grade-distribution-demographics-header">Grade Distribution by Demographics</h2>
    <div>Lorem ipsum</div>
    <select
      id="grade-distribution-demographics-select"
      v-model="selectedDemographic"
      class="my-4"
      @change="onSelectDemographic"
    >
      <option :value="null">Select Demographic</option>
      <template v-for="(group, key) in demographicOptions" :key="key">
        <option
          :id="`grade-distribution-demographics-option-${key}`"
          :disabled="!size(group.options)"
          :value="{'group': key, 'option': get(group.options, 0)}"
        >
          {{ group.label }}
        </option>
      </template>
    </select>
    <highcharts :options="chartSettings"></highcharts>
    <v-row class="d-flex justify-center">
      <v-btn
        id="grade-distribution-demographics-show-btn"
        aria-controls="page-help-notice"
        :aria-expanded="showTable"
        aria-haspopup="true"
        class="font-weight-medium text-no-wrap my-2"
        color="primary"
        :prepend-icon="showTable ? mdiArrowUpCircle : mdiArrowDownCircle"
        size="large"
        variant="text"
        @click="showTable = !showTable"
      >
        {{ showTable ? 'Hide' : 'Show' }} Data Table
      </v-btn>
    </v-row>
    <v-row class="d-flex justify-center">
      <v-expand-transition>
        <v-card v-show="showTable" class="pb-2" width="700">
          <table id="grade-distribution-demo-table" class="border-0 border-t">
            <caption class="font-weight-bold font-size-16 py-3">Class Grade Average by Semester</caption>
            <thead class="bg-grey-lighten-4">
              <tr>
                <th class="font-weight-bold pl-4 py-2" scope="col">Semester</th>
                <th class="font-weight-bold py-2" scope="col">Overall Class Grade Average</th>
                <th class="font-weight-bold py-2" scope="col">Overall Class Count</th>
                <th
                  v-if="size(chartSettings.series) > 1"
                  class="font-weight-bold py-2"
                  scope="col"
                >
                  Average {{ chartSettings.series[1].name }}
                </th>
                <th
                  v-if="size(chartSettings.series) > 1"
                  class="font-weight-bold py-2"
                  scope="col"
                >
                  Count of {{ chartSettings.series[1].name }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(term, index) in chartSettings.xAxis.categories"
                :id="`grade-distribution-demo-table-row-${index}`"
                :key="index"
              >
                <td
                  :id="`grade-distro-demo-table-row-${index}-term`"
                  class="text-no-wrap pl-4 py-1"
                  scope="row"
                >
                  {{ gradeDistribution[index].termName }}
                </td>
                <td :id="`grade-distro-demo-table-row-${index}-grade-0`" class="py-1">{{ chartSettings.series[0]['data'][index].y }}</td>
                <td :id="`grade-distro-demo-table-row-${index}-count-0`" class="py-1">{{ chartSettings.series[0]['data'][index].custom.count }}</td>
                <td
                  v-if="size(chartSettings.series) > 1"
                  :id="`grade-distro-demo-table-row-${index}-grade-1`"
                  class="py-1"
                >
                  {{ chartSettings.series[1]['data'][index].y }}
                </td>
                <td
                  v-if="size(chartSettings.series) > 1"
                  :id="`grade-distro-demo-table-row-${index}-count-1`"
                  class="py-1"
                >
                  {{ chartSettings.series[1]['data'][index].custom.count }}
                </td>
              </tr>
            </tbody>
          </table>
        </v-card>
      </v-expand-transition>
    </v-row>
  </div>
</template>

<script setup>
import {mdiArrowDownCircle, mdiArrowUpCircle} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import {cloneDeep, each, get, replace, round, size} from 'lodash'

export default {
  name: 'DemographicsChart',
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
    courseName: {
      required: true,
      type: String
    },
    gradeDistribution: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    chartSettings: {},
    demographicOptions: {
      'genders.female': {
        label: 'Female',
        options: []
      },
      'genders.male': {
        label: 'Male',
        options: []
      },
      'genders.other': {
        label: 'Other Gender',
        options: []
      },
      underrepresentedMinorityStatus: {
        label: 'Underrepresented Minority',
        options: []
      },
      internationalStatus: {
        label: 'International Students',
        options: []
      },
      transferStatus: {
        label: 'Transfer Students',
        options: []
      },
    },
    selectedDemographic: null,
    showTable: false
  }),
  created() {
    this.chartSettings = cloneDeep(this.chartDefaults)
    this.chartSettings.chart.type = 'line'
    this.chartSettings.legend.squareSymbol = false
    this.chartSettings.legend.symbolHeight = 3
    this.chartSettings.plotOptions.series.lineWidth = 3
    this.chartSettings.title.text = 'Overall Class Grade Average by Semester'
    const courseName = this.courseName
    this.chartSettings.tooltip.formatter = function () {
      const header = `<div id="grade-dist-demo-tooltip-term" class="font-weight-bold font-size-15">${this.x}</div>
          <div id="grade-dist-demo-tooltip-course" class="font-size-13 text-grey-darken-1">${courseName}</div>
          <hr aria-hidden="true" class="mt-1 grade-dist-tooltip-hr" />`
      return (this.points || []).reduce((tooltipText, point, index) => {
        return`${tooltipText}<div id="grade-dist-demo-tooltip-series-${index}" class="font-size-13 mt-1">
          <span aria-hidden="true" class="font-size-16" style="color:${point.color}">\u25AC</span>
          ${point.series.name}: <span class="font-weight-bold">${point.y}</span>
        </div>`
      }, header)
    }
    this.chartSettings.yAxis.labels.format = '{value:.1f}'
    this.chartSettings.yAxis.max = 4
    this.chartSettings.yAxis.min = 0
    this.chartSettings.yAxis.tickInterval = 1
    this.collectDemographicOptions()
    this.loadPrimarySeries()
  },
  methods: {
    collectDemographicOptions() {
      each(this.gradeDistribution, item => {
        each(item, (values, category) => {
          let option = get(this.demographicOptions, category)
          if (option && !size(option['options'])) {
            option['options'] = ['true']
          } else if (category === 'genders') {
            each(values, (vals, subcategory) => {
              option = get(this.demographicOptions, `${category}.${subcategory}`)
              if (option && !size(option['options'])) {
                option['options'] = ['true']
              }
            })
          }
        })
      })
    },
    get,
    getSeriesMarker(series) {
      return {
        'fillColor': 'white',
        'lineColor': series.color,
        'lineWidth': 3,
        'radius': 5,
        'symbol': 'circle'
      }
    },
    loadPrimarySeries() {
      this.chartSettings.colors = [this.colors.primary, this.colors.secondary]
      this.chartSettings.series[0].color = this.colors.primary
      this.chartSettings.series[0].legendSymbol = 'rectangle'
      this.chartSettings.series[0].marker = this.getSeriesMarker(this.chartSettings.series[0])
      this.chartSettings.series[0].name = 'Overall Class Grades'
      each(this.gradeDistribution, item => {
        this.chartSettings.series[0].data.push({
          color: this.colors.primary,
          custom: {count: item.count},
          y: round(item.averageGradePoints, 1)
        })
        this.chartSettings.xAxis.categories.push(this.shortTermName(item.termName))
      })
    },
    onSelectDemographic() {
      if (this.selectedDemographic) {
        const group = get(this.selectedDemographic, 'group')
        const option = get(this.selectedDemographic, 'option')
        const secondarySeries = {
          color: this.colors.secondary,
          data: [],
          legendSymbol: 'rectangle',
          marker: this.getSeriesMarker(this.colors.secondary),
          name: `${get(this.demographicOptions, group)['label']} Grades`
        }
        each(this.gradeDistribution, item => {
          const value = get(item, `${group}`) || get(item, `${group}.${option}`)
          secondarySeries.data.push({
            custom: {count: get(value, 'count', 0)},
            dataLabels: {
              enabled: false
            },
            y: round(get(value, 'averageGradePoints', 0), 1)
          })
        })
        this.chartSettings.series[1] = secondarySeries
      } else if (this.chartSettings.series.length > 1) {
        this.chartSettings.series.pop()
      }
    },
    shortTermName(termName) {
      return replace(termName, /[\d]{4}/g, year => {
        return `'${year.substring(2, 4)}`
      })
    },
    size
  }
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type  -->
<style lang="scss">
.grade-distribution-demographics .highcharts-legend .highcharts-point {
  y: 12;
}
</style>
