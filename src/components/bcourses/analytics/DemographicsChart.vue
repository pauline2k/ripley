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
      <template v-for="(group, key) in demographicOptions">
        <template v-if="size(group.options) === 1">
          <option
            :id="`grade-distribution-demographics-option-${key}-0`"
            :key="`${key}-0`"
            class="border-bottom"
            :value="{'group': key, 'option': group.options[0]}"
          >
            {{ group.label }}
          </option>
        </template>
        <template v-else>
          <optgroup :key="key" :label="group.label">
            <option
              v-for="(option, index) in group.options.sort()"
              :id="`grade-distribution-demographics-option-${key}-${index}`"
              :key="`${key}-${index}`"
              :value="{'group': key, 'option': option}"
            >
              {{ option }}
            </option>
          </optgroup>
        </template>
      </template>
    </select>
    <highcharts :options="chartSettings"></highcharts>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import {cloneDeep, each, get, includes, keys, size, union} from 'lodash'

export default {
  name: 'DemographicsChart',
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
    demographicOptions: {
      transferStatus: {
        label: 'Transfer Student',
        options: []
      },
      underrepresentedMinorityStatus: {
        label: 'Underrepresented Minority',
        options: []
      },
      genders: {
        label: 'Gender',
        options: []
      },
      ethnicities: {
        label: 'Ethnicity',
        options: []
      },
      termsInAttendance: {
        label: 'Terms in Attendance',
        options: []
      },
      visaTypes: {
        label: 'VISA Type',
        options: []
      },
    },
    selectedDemographic: null
  }),
  created() {
    this.chartSettings = cloneDeep(this.chartDefaults)
    this.collectDemographicOptions()
  },
  methods: {
    collectDemographicOptions() {
      const translate = (category, values) => {
        if (includes(['transferStatus', 'underrepresentedMinorityStatus'], category)) {
          return ['true']
        }
        return values
      }
      each(this.gradeDistribution, item => {
        each(item, (values, category) => {
          if (category in this.demographicOptions) {
            let options = this.demographicOptions[category]['options']
            options = union(options, translate(category, keys(values)))
            this.demographicOptions[category]['options'] = options
          }
        })
      })
    },
    onSelectDemographic() {
      if (this.selectedDemographic) {
        const group = get(this.selectedDemographic, 'group')
        const option = get(this.selectedDemographic, 'option')
        const optionLabel = option === 'true' ? '' : `&mdash; ${option}`
        const secondarySeries = {
          data: [],
          name: `${this.demographicOptions[group].label} ${optionLabel}`
        }
        each(this.gradeDistribution, item => {
          secondarySeries.data.push({
            custom: {count: get(item[group][option], 'count', 0)},
            dataLabels: {
              enabled: false
            },
            y: get(item[group][option], 'percentage', 0)
          })
        })
        this.chartSettings.series[1] = secondarySeries
      } else if (this.chartSettings.series.length > 1) {
        this.chartSettings.series.pop()
      }
      this.changeSeriesColor(this.chartSettings)
    },
    size
  }
}
</script>
