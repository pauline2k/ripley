<template>
  <div>
    <Header1 id="page-title" class="sr-only" text="Roster Photos" />
    <div aria-live="polite" class="d-print-none">
      <v-alert
        v-if="error"
        class="ma-3"
        :closable="false"
        density="compact"
        role="none"
        type="warning"
      >
        {{ error }}
      </v-alert>
    </div>
    <div v-if="!contextStore.isLoading && roster">
      <v-container v-if="!error" class="roster-heading d-print-none pb-2" fluid>
        <v-row no-gutters>
          <v-col
            class="py-1"
            cols="12"
            lg="9"
          >
            <div class="d-flex flex-wrap flex-md-nowrap">
              <label for="roster-search" class="sr-only">Input automatically searches upon text entry</label>
              <v-text-field
                id="roster-search"
                v-model="search"
                aria-label="Search students by name or S I D"
                autocomplete="off"
                class="roster-search-input mx-1r my-1"
                density="compact"
                hide-details
                label="Search students by name or SID"
                type="search"
                variant="outlined"
              />
              <select
                v-if="size(roster.sections)"
                id="section-select"
                v-model="selectedSectionId"
                aria-label="Filter by section"
                autocomplete="off"
                class="roster-search-section-select mx-1r my-1"
                @change="onSelectSection"
              >
                <option :value="null">All Sections</option>
                <option
                  v-for="(section, index) in roster.sections"
                  :key="index"
                  :value="section.id"
                >
                  {{ section.name }}
                </option>
              </select>
            </div>
            <div
              aria-live="polite"
              class="position-absolute py-2 mx-1r d-print-none text-subtitle-2"
            >
              {{ pluralize('student', students.length, {0: 'No', 1: 'One'}) }} found
            </div>
          </v-col>
          <v-col
            class="d-flex align-center justify-end py-1"
            cols="12"
            lg="3"
          >
            <ProgressButton
              id="download-csv"
              :action="downloadCsv"
              class="mx-1r roster-btn"
              :disabled="isDownloading || !students.length"
              :in-progress="isDownloading"
              :prepend-icon="mdiDownload"
              variant="outlined"
            >
              Export<span class="sr-only"> CSV file</span>
            </ProgressButton>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col>
            <div class="d-flex align-center justify-end flex-wrap flex-md-nowrap">
              <v-checkbox
                v-model="showOnePhotoPerPage"
                aria-controls="print-roster"
                class="flex-grow-0"
                color="primary"
                density="comfortable"
                hide-details
              >
                <template #label>
                  <span class="mx-1r">Print one student per page</span>
                </template>
              </v-checkbox>
              <v-tooltip
                id="print-button-tooltip"
                v-model="showPrintButtonTooltip"
                :activator-props="{'aria-describedby': (disablePrintButton ? 'print-button-tooltip' : undefined)}"
                :attach="true"
                class="print-button-tooltip"
                content-class="on-surface-variant"
                :eager="disablePrintButton"
                location="left"
                offset="4"
                :open-on-focus="true"
                :persistent="false"
                scroll-strategy="none"
                text="You can print once student images have loaded."
              >
                <template #activator="{props}">
                  <v-btn
                    id="print-roster"
                    :aria-disabled="disablePrintButton"
                    class="roster-btn mx-1r"
                    :class="{'v-btn--disabled': disablePrintButton}"
                    color="primary"
                    :prepend-icon="mdiPrinter"
                    variant="flat"
                    v-bind="props"
                    @click="printRoster"
                  >
                    <span class="ml-2">Print<span class="sr-only"> roster</span></span>
                  </v-btn>
                </template>
              </v-tooltip>
            </div>
          </v-col>
        </v-row>
      </v-container>
      <RosterPhotos
        v-if="size(students)"
        :students="students"
        :show-one-photo-per-page="showOnePhotoPerPage"
      />
      <div aria-live="polite">
        <div v-if="!roster.students.length" class="px-3">
          <v-icon color="warning" :icon="mdiAlertCircleOutline" />
          Students have not yet signed up for this class.
        </div>
        <div v-if="roster.students.length && !students.length" class="px-3">
          <v-icon color="warning" :icon="mdiAlertCircleOutline" />
          No students found matching your query.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {each, filter, map, size, trim} from 'lodash'
import {mdiAlertCircleOutline, mdiDownload, mdiPrinter} from '@mdi/js'
import Header1 from '@/components/utils/Header1.vue'
import ProgressButton from '@/components/utils/ProgressButton'
import RosterPhotos from '@/components/bcourses/roster/RosterPhotos'
import {alertScreenReader, pluralize, printPage} from '@/utils'
import {useContextStore} from '@/stores/context'
import {exportRoster, getRoster} from '@/api/canvas-site'

const contextStore = useContextStore()
const error = ref(undefined)
const isDownloading = ref(false)
const showOnePhotoPerPage = ref(false)
const roster = ref(undefined)
const search = ref(undefined)
const selectedSectionId = ref(null)
const showTooltip = ref(true)
const students = ref(undefined)

const disablePrintButton = computed(() => {
  return !size(students.value) || !!students.value.find(s => !s.hasRosterPhotoLoaded)
})
const showPrintButtonTooltip = defineModel({
  get() {
    return !contextStore.isLoading && showTooltip.value && disablePrintButton.value
  },
  set(value) {
    showTooltip.value = value
  },
  type: Boolean
})

watch(search, () => {
  recalculateStudents()
})

contextStore.loadingStart()

onMounted(() => {
  getRoster(contextStore.currentUser.canvasSiteId).then(
    data => {
      roster.value = data
      students.value = roster.value.students
      each(students.value, s => s.idx = idx(`${s.firstName} ${s.lastName} ${s.studentId}`))
      // If student count is low then tooltip is not necessary.
      const threshold = 36
      showPrintButtonTooltip.value = (students.value.length >= threshold) && disablePrintButton.value
    },
    e => error.value = e
  ).finally(() => contextStore.loadingComplete())
})

const downloadCsv = () => {
  isDownloading.value = true
  exportRoster(contextStore.currentUser.canvasSiteId).then(() => {
    alertScreenReader(`${contextStore.currentUser.canvasSiteName} CSV downloaded`)
    setTimeout(() => isDownloading.value = false, 1500)
  })
}

const onSelectSection = () => {
  recalculateStudents()
}

const recalculateStudents = () => {
  const normalizedPhrase = idx(search.value)
  if (normalizedPhrase || selectedSectionId.value) {
    students.value = filter(roster.value.students, student => {
      let showStudent = !normalizedPhrase || student.idx.includes(normalizedPhrase)
      if (selectedSectionId.value) {
        showStudent = showStudent && map(student.sections || [], 'id').includes(selectedSectionId.value)
      }
      return showStudent
    })
  } else {
    students.value = roster.value.students
  }
}

const idx = value => {
  return value && trim(value).replace(/[^\w\s]/gi, '').toLowerCase()
}

const printRoster = () => {
  if (disablePrintButton.value) {
    return false
  }
  printPage(`${idx(contextStore.currentUser.canvasSiteName).replace(/\s/g, '-')}_roster`)
}
</script>

<style scoped lang="scss">
.print-button-tooltip {
  z-index: 0 !important;
}
.roster-btn {
  margin: 1px;
  width: 7rem;
}
.roster-heading {
  min-width: 395px;
  z-index: 0;
}
.roster-search-input {
  flex: 1 1 50%;
}
.roster-search-section-select {
  flex: 1 1 50%;
}
.z-index-100 {
  z-index: 100;
}
</style>
