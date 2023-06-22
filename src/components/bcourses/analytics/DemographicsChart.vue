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
      <optgroup
        v-for="(options, group) in demographicOptions"
        :key="group"
        :label="optionGroupLabels[group]"
      >
        <option
          v-for="(option, index) in options"
          :id="`grade-distribution-demographics-option-${index}`"
          :key="index"
          :value="{'group': group, 'option': option}"
        >
          {{ option }}
        </option>
      </optgroup>
    </select>
    <highcharts :options="chartSettings"></highcharts>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'

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
    demographicOptions: {},
    optionGroupLabels: {
      ethnicities: 'Ethnicity',
      genders: 'Gender',
      transferStatus: 'Transfer Student',
      underrepresentedMinorityStatus: 'Underrepresented Minority',
      visaTypes: 'VISA Type'
    },
    selectedDemographic: null
  }),
  created() {
    this.chartSettings = this.$_.cloneDeep(this.chartDefaults)
    this.$_.each(this.gradeDistribution, item => {
      this.$_.each(item, (values, category) => {
        if (category in this.demographicOptions) {
          this.demographicOptions[category] = this.$_.union(this.demographicOptions[category], this.$_.keys(values))
        } else {
          this.demographicOptions[category] = this.$_.keys(values)
        }
      })
    })
  },
  methods: {
    onSelectDemographic() {
      if (this.selectedDemographic) {
        const group = this.$_.get(this.selectedDemographic, 'group')
        const option = this.$_.get(this.selectedDemographic, 'option')
        const secondarySeries = {
          data: [],
          name: `${this.optionGroupLabels[group]} &mdash; ${option}`
        }
        this.$_.each(this.gradeDistribution, item => {
          const pointValue = this.$_.get(item[group][option], 'percentage', 0)
          secondarySeries.data.push({
            dataLabels: {
              enabled: false
            },
            y: pointValue
          })
        })
        this.chartSettings.series[1] = secondarySeries
      } else if (this.chartSettings.series.length > 1) {
        this.chartSettings.series.pop()
      }
      this.changeSeriesColor(this.chartSettings)
    }
  }
}
</script>
