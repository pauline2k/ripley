<template>
  <div class="pa-5">
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
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import {cloneDeep, each, get, size} from 'lodash'

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
    selectedDemographic: null
  }),
  created() {
    this.chartSettings = cloneDeep(this.chartDefaults)
    this.chartSettings.chart.type = 'line'
    this.chartSettings.series[0].marker = this.getSeriesMarker(this.chartSettings.series[0])
    this.collectDemographicOptions()
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
    onSelectDemographic() {
      if (this.selectedDemographic) {
        const group = get(this.selectedDemographic, 'group')
        const option = get(this.selectedDemographic, 'option')
        const secondarySeries = {
          color: this.colors.secondary,
          data: [],
          marker: this.getSeriesMarker(this.colors.secondary),
          name: get(this.demographicOptions, group)['label']
        }
        each(this.gradeDistribution, item => {
          const value = get(item, `${group}`) || get(item, `${group}.${option}`)
          secondarySeries.data.push({
            custom: {count: get(value, 'count', 0)},
            dataLabels: {
              enabled: false
            },
            y: get(value, 'percentage', 0)
          })
        })
        this.chartSettings.series[1] = secondarySeries
      } else if (this.chartSettings.series.length > 1) {
        this.chartSettings.series.pop()
      }
    },
    size
  }
}
</script>
