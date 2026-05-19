<template>
  <div class="pa-5">
    <div>
      <h2 id="grade-distribution-enrollment-header">Grade Distribution by Prior Class Enrollment</h2>
      <div>
        The grade distribution chart displays available grades at the end of the current and prior semesters.
        Search for a prerequisite course to compare side-by-side final grades of all students taking this course and
        those who have taken the prerequisite.
      </div>
      <v-row no-gutters>
        <v-col cols="12" md="4" sm="6">
          <div class="grade-dist-enroll-course-search d-flex align-center my-3">
            <v-autocomplete
              id="grade-distribution-enrollment-course-search"
              v-model="selectedCourse"
              auto-select-first
              autocomplete="off"
              bg-color="white"
              class="text-upper mr-2"
              density="compact"
              :disabled="isLoadingPriorEnrollments || isEmpty(get(gradeDistribution, get(selectedTerm, 'id')))"
              :error="!suppressValidation && !isEmpty(courseSearchErrors)"
              :error-messages="!suppressValidation ? courseSearchErrors : []"
              hide-details
              hide-no-data
              :items="courseSuggestions"
              label="Search Classes..."
              :loading="isSearching ? 'primary' : false"
              :menu-icon="undefined"
              :search="courseSearchText"
              variant="outlined"
              @blur="selectedCourse = toUpper(courseSearchText)"
              @change="suppressValidation = false"
              @update:search="text => courseSearchText = text"
            >
              <template #item="{props, item}">
                <v-list-item
                  v-bind="props"
                  class="py-0 my-0"
                  density="compact"
                  height="unset"
                  min-height="30"
                  :title="item.raw"
                  :value="item.raw"
                />
              </template>
            </v-autocomplete>
            <v-btn
              id="grade-distribution-enroll-add-class-btn"
              class="font-size-13"
              color="primary"
              :disabled="!selectedCourse || isLoadingPriorEnrollments || isEmpty(get(gradeDistribution, get(selectedTerm, 'id')))"
              @click="onClickAddCourse"
            >
              Add Class
            </v-btn>
          </div>
          <div
            v-if="selectedCourse && insufficientData"
            class="grade-dist-enroll-course-search alert mb-3 px-4"
          >
            <div class="d-flex flex-no-wrap">
              <v-icon class="canvas-notice-icon mr-2" :icon="mdiAlert" />
              <span>
                No <span :class="{'demo-mode-blur': isDemoMode}">{{ courseName }}</span> {{ get(selectedTerm, 'name') }}
                students were previously enrolled in {{ selectedCourse }}.
              </span>
            </div>
          </div>
          <div>
            <v-checkbox
              v-model="collapseLetterGrades"
              class="font-weight-medium text-no-wrap my-2"
              color="primary"
              density="compact"
              hide-details="auto"
              label="Collapse letter grades"
              @change="refresh"
            />
          </div>
        </v-col>
        <v-col
          class="align-self-end d-flex justify-center px-2"
          cols="12"
          md="4"
          sm="6"
        >
          <v-btn
            id="grade-distribution-enrollment-show-defs-btn"
            aria-controls="grade-distribution-enrollment-definitions"
            :aria-expanded="showChartDefinitions"
            aria-haspopup="true"
            class="font-weight-medium text-no-wrap my-2"
            color="primary"
            :prepend-icon="showChartDefinitions ? mdiArrowUpCircle : mdiArrowDownCircle"
            size="large"
            variant="text"
            @click="showChartDefinitions = !showChartDefinitions"
          >
            {{ showChartDefinitions ? 'Hide' : 'Show' }} Chart Definitions
          </v-btn>
        </v-col>
      </v-row>
      <v-row class="d-flex justify-center" no-gutters>
        <ChartDefinitions id="grade-distribution-enrollment-definitions" :is-expanded="showChartDefinitions" />
      </v-row>
      <hr aria-hidden="true" class="mb-3">
      <div class="position-relative">
        <select
          v-if="size(terms)"
          :value="get(selectedTerm, 'id')"
          autocomplete="off"
          class="position-absolute grade-dist-enroll-term-select"
          :disabled="isEmpty(gradeDistribution)"
          @change="onSelectTerm"
        >
          <option
            v-for="(term, index) in terms"
            :key="index"
            :value="term.id"
          >
            {{ term.name }}
          </option>
        </select>
      </div>
    </div>
    <v-overlay
      v-model="isLoadingPriorEnrollments"
      class="align-center justify-center"
      contained
      persistent
    >
      <PageLoadProgress v-if="isLoadingPriorEnrollments" color="primary" />
    </v-overlay>
    <Chart :options="chartOptions" />
    <v-row v-if="selectedTerm" class="d-flex justify-center">
      <v-btn
        id="grade-distribution-enrollments-show-btn"
        aria-controls="grade-distribution-enroll-table-container"
        :aria-expanded="showTable"
        aria-haspopup="true"
        class="font-weight-medium text-no-wrap my-2"
        color="primary"
        :disabled="isEmpty(get(gradeDistribution, get(selectedTerm, 'id')))"
        :prepend-icon="showTable ? mdiArrowUpCircle : mdiArrowDownCircle"
        size="large"
        variant="text"
        @click="showTable = !showTable"
      >
        {{ showTable ? 'Hide' : 'Show' }} Data Table
      </v-btn>
    </v-row>
    <v-row v-if="selectedTerm" class="d-flex justify-center">
      <v-expand-transition>
        <v-card
          v-show="showTable"
          id="grade-distribution-enroll-table-container"
          class="pb-2"
          width="700"
        >
          <table id="grade-distribution-enroll-table" class="border-0 border-t">
            <caption
              v-if="chartOptions.title"
              class="font-weight-bold font-size-16 py-3"
              v-html="chartOptions.title.text"
            />
            <thead class="bg-grey-lighten-4">
              <tr>
                <th class="font-weight-bold pl-4 py-2" scope="col" rowspan="2">Grade</th>
                <template v-for="(series, index) in chartOptions.series" :key="index">
                  <th
                    class="grade-distribution-table-border font-weight-bold text-center pt-2 pb-0"
                    :class="{'demo-mode-blur': isDemoMode && index === 0}"
                    colspan="2"
                    scope="col"
                  >
                    {{ series.name }}
                  </th>
                </template>
              </tr>
              <tr>
                <template v-for="(series, index) in chartOptions.series" :key="index">
                  <th class="grade-distribution-table-border font-weight-bold pt-0" scope="col">Ratio</th>
                  <th class="text-right font-weight-bold pt-0" scope="col">Count</th>
                </template>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(grade, gradeIndex) in chartOptions.xAxis[0].categories"
                :id="`grade-distribution-enroll-table-row-${gradeIndex}`"
                :key="gradeIndex"
              >
                <td
                  :id="`grade-distro-enroll-table-row-${gradeIndex}-grade`"
                  class="pl-4 py-1"
                  scope="row"
                >
                  {{ grade }}
                </td>
                <template v-for="(series, index) in chartOptions.series" :key="index">
                  <td
                    :id="`grade-distro-enroll-table-row-${gradeIndex}-ratio-${index}`"
                    class="py-1"
                  >
                    {{ get(series, `data.${gradeIndex}.y`, 0) }}%
                  </td>
                  <td
                    :id="`grade-distro-enroll-table-row-${gradeIndex}-count-${index}`"
                    class="text-right py-1"
                  >
                    {{ get(series, `data.${gradeIndex}.custom.count`, 0) }}
                  </td>
                </template>
              </tr>
            </tbody>
            <tfoot>
              <tr id="grade-distribution-enroll-table-row-totals">
                <th class="pl-4 py-1" scope="row">Totals</th>
                <template v-for="(series, index) in chartOptions.series" :key="index">
                  <td
                    :id="`grade-distro-enroll-table-row-totals-ratio-${index}`"
                    class="font-weight-medium py-1"
                  >
                    {{ round(sumBy(series.data, 'y')) }}%
                  </td>
                  <td
                    :id="`grade-distro-enroll-table-row-totals-count-${index}`"
                    class="text-right font-weight-medium py-1"
                  >
                    {{ sumBy(series.data, 'custom.count') }}
                  </td>
                </template>
              </tr>
            </tfoot>
          </table>
        </v-card>
      </v-expand-transition>
    </v-row>
  </div>
</template>

<script lang="ts" setup>
import type {PropType} from 'vue'
import type {HighchartsOptions} from '@/lib/highcharts'
import {Chart} from 'highcharts-vue'
import {debounce, each, find, get, includes, isEmpty, merge, round, size, sumBy, toUpper} from 'lodash'
import {mdiAlert, mdiArrowDownCircle, mdiArrowUpCircle} from '@mdi/js'
import {nextTick, onMounted, ref, watch} from 'vue'
import {useContextStore} from '@/stores/context'
import ChartDefinitions from '@/components/bcourses/analytics/ChartDefinitions.vue'
import PageLoadProgress from '@/components/utils/PageLoadProgress.vue'
import {CHART_COLORS, getDefaultChartOptions} from '@/lib/highcharts'
import {getPriorEnrollmentGradeDistribution, searchCourses} from '@/api/grade-distribution'
import {Term} from '@/lib/types'

const props = defineProps({
  courseName: {
    required: true,
    type: String
  },
  gradeDistribution: {
    required: true,
    type: Object
  },
  isDemoMode: {
    required: false,
    type: Boolean
  },
  terms: {
    required: true,
    type: Array as PropType<Term[]>
  }
})

const chartOptions = ref<HighchartsOptions>(merge(
  getDefaultChartOptions(),
  {
    chart: {
      type: 'column'
    },
    legend: {
      enabled: get(props.terms, 0) && !isEmpty(get(props.gradeDistribution, get(props.terms, 0).id)),
      symbolHeight: 12,
      useHTML: true
    },
    series: {
      lineWidth: 0,
      states: {
        hover: {
          lineWidthPlus: 0
        }
      }
    },
    title: {
      widthAdjust: -200
    },
    tooltip: {
      distance: 12
    },
    yAxis: [
      {
        labels: {
          format: '{value}%'
        }
      }
    ]
  }
))
const collapseLetterGrades = ref(false)
const currentUser = useContextStore().currentUser
const courseSearchText = ref()
const courseSuggestions = ref([])
const courseSearchErrors = ref([])
const insufficientData = ref(false)
const isLoadingPriorEnrollments = ref(false)
const isSearching = ref(false)
const pendingCourseSearch = ref<AbortController>()
const priorEnrollmentGradeDistribution = ref({})
const selectedCourse = ref()
const selectedTerm = ref()
const showChartDefinitions = ref(false)
const showTable = ref(false)
const suppressValidation = ref(true)

watch(courseSearchText, (newVal, oldVal) => {
  if (newVal) {
    if (newVal !== oldVal) {
      debounce(search, 300)()
    }
  }
})

watch(() => props.isDemoMode, () => {
  setChartTitle()
  setLegendLabel()
  setTooltipFormatter()
})

watch(selectedTerm, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    insufficientData.value = false
  }
})

onMounted(() => {
  selectedTerm.value = get(props.terms, 0)
  setLegendLabel()
  setTooltipFormatter()
  loadPrimarySeries(CHART_COLORS.primary)
  setChartTitle()
})

const collapse = (grade) => {
  const alphanumericMatch = grade && grade.match(/^\w+/)
  if (alphanumericMatch && alphanumericMatch.length) {
    return alphanumericMatch[0]
  }
}

const getDataLabel = (yVal, color) => {
  if (size(chartOptions.value.series) === 1) {
    const displayAboveColumn = yVal < 2
    return {
      color: displayAboveColumn ? color : 'white',
      enabled: true,
      format: '{y}%',
      style: {
        textOutline: 'none'
      },
      y: displayAboveColumn ? 2 : 22
    }
  } else {
    return {
      enabled: false
    }
  }
}

const loadPrimarySeries = (color: string, showLabels=true) => {
  chartOptions.value.series[0] = {
    color,
    data: [],
    name: `${get(selectedTerm.value, 'name')} ${props.courseName}`,
    type: 'column'
  }
  chartOptions.value.xAxis[0].categories = []
  const gradeDistribution = []
  each(props.gradeDistribution[get(selectedTerm.value, 'id')], item => {
    const displayGrade = collapseLetterGrades.value ? collapse(item.grade) : item.grade
    if (gradeDistribution.length && gradeDistribution[gradeDistribution.length - 1].grade === displayGrade) {
      gradeDistribution[gradeDistribution.length - 1].count += item.count
      gradeDistribution[gradeDistribution.length - 1].percentage += item.percentage
    } else {
      gradeDistribution.push({
        grade: displayGrade,
        count: item.count,
        percentage: item.percentage
      })
    }
  })
  each(gradeDistribution, item => {
    chartOptions.value.series[0].data.push({
      color: color,
      custom: {
        count: item.count
      },
      dataLabels: showLabels ? getDataLabel(item.y, color) : {enabled: false},
      y: round(item.percentage, 1)
    })
    chartOptions.value.xAxis[0].categories = chartOptions.value.xAxis[0].categories || []
    const displayGrade = collapseLetterGrades.value ? collapse(item.grade) : item.grade
    if (!includes(chartOptions.value.xAxis[0].categories, displayGrade)) {
      chartOptions.value.xAxis[0].categories.push(displayGrade)
    }
  })
  chartOptions.value.plotOptions.series.dataLabels = {
    enabled: showLabels
  }
}

const loadPriorEnrollments = () => {
  type summary = {custom: {count: number}, dataLabels: {enabled: boolean}, y: number}
  const data: summary[] = []
  const gradeDistribution = []
  each(priorEnrollmentGradeDistribution.value[get(selectedTerm.value, 'id')], item => {
    const displayGrade = collapseLetterGrades.value ? collapse(item.grade) : item.grade
    if (gradeDistribution.length && gradeDistribution[gradeDistribution.length - 1].grade === displayGrade) {
      gradeDistribution[gradeDistribution.length - 1].priorEnrollCount += item.priorEnrollCount
      gradeDistribution[gradeDistribution.length - 1].priorEnrollPercentage += item.priorEnrollPercentage
    } else {
      gradeDistribution.push({
        grade: displayGrade,
        priorEnrollCount: item.priorEnrollCount,
        priorEnrollPercentage: item.priorEnrollPercentage
      })
    }
  })
  each(gradeDistribution, item => {
    if (chartOptions.value.xAxis && includes(chartOptions.value.xAxis[0].categories, item.grade)) {
      while (chartOptions.value.xAxis[0].categories.indexOf(item.grade) > data.length) {
        data.push(null)
      }
      data.push({
        custom: {
          count: get(item, 'priorEnrollCount', 0)
        },
        dataLabels: {enabled: false},
        y: round(get(item, 'priorEnrollPercentage', 0), 1)
      })
    }
  })
  chartOptions.value.series[1] = {
    color: CHART_COLORS.secondary,
    data,
    name: `Have taken ${selectedCourse.value}`,
    type: 'column'
  }
}

const onClickAddCourse = () => {
  if (selectedCourse.value) {
    isLoadingPriorEnrollments.value = true
    getPriorEnrollmentGradeDistribution(currentUser.canvasSiteId, selectedCourse.value).then(response => {
      courseSearchText.value = undefined
      priorEnrollmentGradeDistribution.value = response
      isLoadingPriorEnrollments.value = false
      refresh()
    })
  }
}

const onSelectTerm = e => {
  const termId = e.target.value
  selectedTerm.value = find(props.terms, {'id': termId})
  refresh()
}

const refresh = () => {
  if (get(priorEnrollmentGradeDistribution.value, get(selectedTerm.value, 'id'))) {
    loadPrimarySeries(CHART_COLORS.primary, false)
    loadPriorEnrollments()
    insufficientData.value = false
  } else {
    chartOptions.value.series = []
    loadPrimarySeries(CHART_COLORS.primary)
    insufficientData.value = true
  }
  setChartTitle()
}

const search = () => {
  isSearching.value = true
  if (pendingCourseSearch.value) {
    pendingCourseSearch.value.abort()
  }
  pendingCourseSearch.value = new AbortController()
  searchCourses(toUpper(courseSearchText.value), pendingCourseSearch.value).then(data => {
    courseSuggestions.value = data.results
    isSearching.value = false
  }).catch(() => {
    nextTick(() => isSearching.value = false)
  })
}

const setChartTitle = () => {
  chartOptions.value.title = chartOptions.value.title || {}
  if (size(chartOptions.value.series) > 1) {
    chartOptions.value.title.useHTML = true
    chartOptions.value.title.text = `Relation of <span ${props.isDemoMode ? 'class="demo-mode-blur"' : ''}>
      ${selectedTerm.value.name} ${props.courseName}
      </span> Students Who Have Taken ${selectedCourse.value} to Overall Class`
  } else {
    chartOptions.value.title.useHTML = false
    chartOptions.value.title.text = `Overall Class Grade Distribution&mdash;${selectedTerm.value.name}`
  }
}

const setLegendLabel = () => {
  chartOptions.value.legend = chartOptions.value.legend || {}
  chartOptions.value.legend.labelFormat = `{#if (eq index 0)}<span ${props.isDemoMode ? 'class="demo-mode-blur"' : ''}>{else}<span>{/if}
      {name}
    </span> grades`
}

const setTooltipFormatter = () => {
  const courseName = props.courseName
  const isDemoMode = props.isDemoMode
  chartOptions.value.tooltip = chartOptions.value.tooltip || {}
  chartOptions.value.tooltip.formatter = function() {
    const header = `<div id="grade-dist-enroll-tooltip-grade" class="font-weight-bold font-size-15">${this.x} Grade</div>
        <div id="grade-dist-enroll-tooltip-course" class="font-size-13 text-grey-darken-1">
          <span aria-hidden="true" class="grade-dist-enroll-tooltip-symbol" style="color:${this.color}">\u25A0</span>
          <span ${isDemoMode ? 'class="demo-mode-blur"' : ''}>${courseName}</span>
        </div>
        <div class="font-size-13 mb-2">
          Ratio of class: <span id="grade-dist-enroll-tooltip-series-0-value" class="font-weight-bold">${this.y}%</span>
        </div>
        <hr aria-hidden="true" class="mb-2 ${size(this.points) <= 1 ? 'd-none' : ''}" />`
    return (this.points ? this.points.slice(1) || [] : []).reduce((tooltipText, plot, index) => {
      return`${tooltipText}<div id="grade-dist-enroll-tooltip-series-${index + 1}" class="font-size-13 pb-2">
        <div class="text-grey-darken-1 text-uppercase">
          <span aria-hidden="true" class="grade-dist-enroll-tooltip-symbol" style="color:${plot.color}">\u25A0</span>
          ${plot.series.name}
        </div
        <div>
          Ratio of class: <span id="grade-dist-enroll-tooltip-series-${index + 1}-value" class="font-weight-bold">${plot.y}%</span>
        </div>
      </div>`
    }, header)
  }
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type  -->
<style lang="scss">
.grade-dist-enroll-tooltip-symbol {
  display: inline-block;
  font-size: 1.25rem !important;
  line-height: 1.1px;
  position: relative;
  top: 1px;
  width: 16px;
}
.v-autocomplete.text-upper input {
  text-transform: uppercase !important;
}
</style>

<style lang="scss" scoped>
.grade-dist-enroll-course-search {
  min-width: 240px;
}
.grade-dist-enroll-term-select {
  right: 0;
  top: 5px;
  z-index: 100;
}
</style>
