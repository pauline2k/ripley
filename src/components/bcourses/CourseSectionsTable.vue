<template>
  <div class="bg-white">
    <div
      v-if="mode === 'createCourseForm' && sections.length > 1"
      class="pb-2 pl-4 pt-3"
    >
      <v-checkbox
        :id="`select-all-toggle-${sections[0].id}`"
        v-model="allSelected"
        density="compact"
        hide-details
        :indeterminate="indeterminate"
        @change="toggleAll"
      >
        <template #label>
          <span class="font-weight-medium ml-1">
            Select {{ allSelected ? 'None' : 'All' }}
            <span class="sr-only">of the course sections</span>
          </span>
        </template>
      </v-checkbox>
    </div>
    <table :id="id" class="border-0 border-b-md border-t-md">
      <caption class="sr-only">{{ tableCaption }}</caption>
      <thead class="bg-grey-lighten-4">
        <tr>
          <th
            v-if="mode === 'createCourseForm'"
            class="pl-4 pr-0 td-checkbox"
            scope="col"
          >
            Action
          </th>
          <th class="td-course-code" scope="col">Course</th>
          <th class="td-section-name" scope="col">Section</th>
          <th class="td-section-id text-no-wrap" scope="col">Section ID</th>
          <th :class="{'td-schedule': hasSectionScheduleData, 'td-shrink-to-fit': !hasSectionScheduleData}" scope="col">
            Schedule
          </th>
          <th :class="{'td-meeting-location': hasSectionScheduleData, 'td-shrink-to-fit': !hasSectionScheduleData}" scope="col">
            Location
          </th>
          <th class="td-instructors">Instructors</th>
          <th v-if="mode !== 'createCourseForm' && mode !== 'preview'" class="td-actions" scope="col">
            <span v-if="mode !== 'preview'" class="mr-5">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody v-for="(section, sectionIndex) in displayableSections" :key="section.id">
        <tr :id="`${id}-${section.id}`" :class="sectionDisplayClass[section.id]">
          <td v-if="mode === 'createCourseForm'" :id="`${id}-${section.id}-action`" class="align-top td-checkbox pl-3 pr-0 py-0">
            <v-checkbox
              :id="`template-canvas-manage-sections-checkbox-${section.id}`"
              v-model="selected"
              :aria-label="`${section.courseCode}, ${section.name}`"
              class="ml-2"
              density="compact"
              hide-details
              name="section-section-id"
              :value="section.id"
            />
          </td>
          <td :id="`${id}-${section.id}-course`" class="td-course-code text-no-wrap">
            <label v-if="mode === 'createCourseForm'" :for="`template-canvas-manage-sections-checkbox-${section.id}`">
              <span class="sr-only">Course code </span>{{ section.courseCode }}
            </label>
            <span v-if="mode !== 'createCourseForm'">
              <span class="sr-only">Course code </span>{{ section.courseCode }}
            </span>
          </td>
          <td :id="`${id}-${section.id}-name`" class="td-section-name">
            <label
              v-if="mode === 'createCourseForm'"
              :for="`template-canvas-manage-sections-checkbox-${section.id}`"
            >
              <span class="sr-only">Section name </span>{{ section.name }}
            </label>
            <span v-if="mode !== 'createCourseForm'">{{ section.name }}</span>
            <span v-if="mode === 'currentStaging' && section.nameDiscrepancy && section.stagedState !== 'update'" class="sr-only">
              The section name in bCourses no longer matches the Student Information System.
              Use the "Update" button to rename your bCourses section name to match SIS.
            </span>
          </td>
          <td :id="`${id}-${section.id}-id`" class="td-section-id">
            <span class="sr-only">Section ID </span>{{ section.id }}
          </td>
          <td :id="`${id}-${section.id}-schedule`" :class="{'td-schedule': hasSectionScheduleData, 'td-shrink-to-fit': !hasSectionScheduleData}">
            <span class="sr-only">Schedule, </span>
            <template v-if="filterRecurring(section, 'schedule').length">
              <span
                v-for="(schedule, index) in uniqBy(filterRecurring(section, 'schedule'), 'schedule')"
                :key="index"
                class="d-block"
              >
                <span aria-hidden="true">{{ schedule.schedule }}</span>
                <span class="sr-only">{{ describeSchedule(schedule) }}</span>
              </span>
            </template>
            <template v-else>
              <span aria-hidden="true">&mdash;</span>
              <span class="sr-only">blank</span>
            </template>
          </td>
          <td :id="`${id}-${section.id}-location`" :class="{'td-meeting-location': hasSectionScheduleData, 'td-shrink-to-fit': !hasSectionScheduleData}">
            <span class="sr-only">Location, </span>
            <template v-if="filterRecurring(section, 'buildingName').length">
              <span
                v-for="(schedule, index) in filterRecurring(section, 'buildingName')"
                :key="index"
                class="d-block"
              >
                {{ schedule.buildingName }} {{ schedule.roomNumber }}
              </span>
            </template>
            <template v-else>
              <span aria-hidden="true">&mdash;</span>
              <span class="sr-only">blank</span>
            </template>
          </td>
          <td :id="`${id}-${section.id}-instructors`" class="td-instructors">
            <div class="sr-only-in-standard-viewport">Instructors:</div>
            <template v-if="filter(section.instructors, 'name').length">
              <div class="instructors">
                <span
                  v-for="instructor in section.instructors"
                  :key="instructor.uid"
                  class="d-block"
                >
                  {{ instructor.name }} <span class="sr-only">,</span>
                </span>
              </div>
            </template>
            <template v-else>
              <span aria-hidden="true">&mdash;</span>
              <span class="sr-only">blank</span>
            </template>
          </td>
          <td
            v-if="!['createCourseForm', 'preview'].includes(mode)"
            :id="`${id}-${section.id}-actions`"
            class="td-actions vertical-middle"
          >
            <!-- Current Staging Actions -->
            <div v-if="mode === 'currentStaging' && section.isCourseSection" class="d-flex flex-nowrap responsive-justify-end">
              <v-btn
                v-if="section.nameDiscrepancy && section.stagedState !== 'update'"
                :id="`section-${section.id}-update-btn`"
                :aria-label="`Update '${section.courseCode} ${section.name}' section name`"
                class="ml-1"
                color="primary"
                density="compact"
                text="Update"
                @click="() => stageUpdate(section)"
              />
              <v-btn
                v-if="section.stagedState === 'update'"
                :id="`section-${section.id}-undo-update-btn`"
                :aria-label="`Undo update '${section.courseCode} ${section.name}' section name`"
                class="button-undo-delete ml-1"
                density="compact"
                text="Undo Update"
                @click="() => unstage(section, sectionIndex, 'undo-update')"
              />
              <v-btn
                v-if="section.stagedState !== 'update'"
                :id="`section-${section.id}-unlink-btn`"
                :aria-label="`Unlink '${section.courseCode} ${section.name}' from the course site`"
                class="ml-1"
                color="primary"
                density="compact"
                text="Unlink"
                @click="() => stageDeletePreCheck(section, sectionIndex)"
              />
            </div>
            <div v-if="mode === 'currentStaging' && !section.isCourseSection">
              <v-btn
                :id="`section-${section.id}-undo-link-btn`"
                :aria-label="`Undo link '${section.courseCode} ${section.name}' to the course site`"
                class="button-undo-add ml-1"
                density="compact"
                text="Undo Link"
                @click="() => unstage(section, sectionIndex, 'undo-link')"
              />
            </div>
            <!-- Available Staging Actions -->
            <div v-if="mode === 'availableStaging' && section.isCourseSection && section.stagedState === 'delete'">
              <v-btn
                :id="`section-${section.id}-undo-unlink-btn`"
                :aria-label="`Undo unlink '${section.courseCode} ${section.name}' from the course site`"
                class="button-undo-delete ml-1"
                density="compact"
                text="Undo Unlink"
                @click="() => unstage(section, sectionIndex, 'undo-unlink')"
              >
                Undo Unlink
              </v-btn>
            </div>
            <div v-if="mode === 'availableStaging' && !section.isCourseSection && section.stagedState === 'add'" class="mr-5">
              Linked <span class="sr-only">to pending list of new sections</span>
            </div>
            <div v-if="mode === 'availableStaging' && !section.isCourseSection && !section.stagedState">
              <v-btn
                :id="`section-${section.id}-link-btn`"
                :aria-label="`Link '${section.courseCode} ${section.name}' to the course site`"
                class="ml-1"
                :class="{'button-undo-add': section.stagedState === 'add'}"
                density="compact"
                text="Link"
                @click="() => stageAdd(section, sectionIndex)"
              />
            </div>
            <div v-if="mode === 'availableStaging' && section.isCourseSection && !section.stagedState" class="sr-only">No action available</div>
          </td>
        </tr>
        <tr
          v-if="showUpdateButton(section)"
          :id="`template-sections-table-row-${mode.toLowerCase()}-${section.id}-discrepancy`"
          aria-hidden="true"
          :class="sectionDisplayClass[section.id]"
        >
          <td class="border-none" />
          <td :id="`${id}-${section.id}-discrepancy`" class="border-none" colspan="6">
            <div>
              <v-icon class="sited-icon mr-1" :icon="mdiInformationVariantCircle" />
              The section name in bCourses no longer matches the Student Information System.
              Use the "Update" button to rename your bCourses section name to match SIS.
            </div>
          </td>
        </tr>
        <tr
          v-if="!['currentStaging', 'preview'].includes(mode) && size(section.canvasSites)"
          :id="`template-sections-table-row-${mode.toLowerCase()}-${section.id}-warning`"
          :class="sectionDisplayClass[section.id]"
        >
          <td class="border-top-zero pa-0" />
          <td
            :id="`${id}-${section.id}-warning`"
            colspan="6"
            class="border-top-zero pb-4 pt-0"
          >
            <div v-if="section.canvasSites.length === 1" class="align-center d-flex">
              <div class="section-in-use-icon">
                <v-icon
                  color="error"
                  :icon="mdiAlert"
                  size="medium"
                />
              </div>
              <div class="align-center d-flex">
                <OutboundLink
                  :id="`${id}-${section.id}-warning-link`"
                  class="mx-1"
                  :hide-icon="true"
                  :href="`${config.canvasApiUrl}/courses/${section.canvasSites[0].canvasSiteId}`"
                >
                  bCourses site {{ section.canvasSites[0].name }}
                </OutboundLink>
                includes this section.
              </div>
            </div>
            <div v-if="section.canvasSites.length > 1">
              <div class="align-center d-flex">
                <div class="section-in-use-icon">
                  <v-icon
                    color="error"
                    :icon="mdiAlert"
                    size="medium"
                  />
                </div>
                <div :id="`${id}-${section.id}-warnings-list-label`">
                  The following bCourses sites include this section.
                </div>
              </div>
              <div class="ml-6 pt-1">
                <ul :aria-labelledby="`${id}-${section.id}-warnings-list-label`" class="sites-container">
                  <li v-for="(canvasSite, index) in section.canvasSites" :key="index">
                    <OutboundLink :id="`${id}-${section.id}-warning-link`" :href="`${config.canvasApiUrl}/courses/${canvasSite.canvasSiteId}`">{{ canvasSite.name }}</OutboundLink>
                  </li>
                </ul>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
      <tbody v-if="mode === 'preview' && sections.length < 1">
        <tr :id="`${id}-no-current-sections-row`">
          <td :id="`${id}-no-current-sections`" colspan="7">There are no currently maintained official sections in this course site.</td>
        </tr>
      </tbody>
      <tbody v-if="mode === 'currentStaging' && noCurrentSections()">
        <tr :id="`${id}-no-remaining-sections-row`">
          <td :id="`${id}-no-remaining-sections`" colspan="7">No official sections will remain in course site</td>
        </tr>
      </tbody>
    </table>
    <AreYouSureModal
      v-model="showAreYouSureModal"
      button-label-confirm="Proceed"
      :function-cancel="stageDeleteCancel"
      :function-confirm="stageDeleteProceed"
      modal-header="Warning"
      modal-header-class="font-size-20 text-error"
      text="You are unlinking the section(s) in which you are enrolled. Proceeding will result in loss of access to this bCourses site."
    />
  </div>
</template>

<script lang="ts" setup>
import moment from 'moment'
import type {PropType} from 'vue'
import {computed, onMounted, ref, watch} from 'vue'
import {each, filter, find, get, includes, map, size, uniqBy} from 'lodash'
import {mdiAlert, mdiInformationVariantCircle} from '@mdi/js'
import AreYouSureModal from '@/components/utils/AreYouSureModal.vue'
import OutboundLink from '@/components/utils/OutboundLink.vue'
import {oxfordJoin, putFocusNextTick} from '@/utils'
import {SectionEdit} from '@/lib/types'
import {useContextStore} from '@/stores/context.js'

export type SectionAndIndex = {
  section: SectionEdit,
  index: number
}

const props = defineProps({
  id: {
    default: 'template-sections-table',
    required: false,
    type: String
  },
  mode: {
    required: true,
    type: String
  },
  rowClassLogic: {
    default: () => '',
    required: false,
    type: Function
  },
  rowDisplayLogic: {
    default: () => true,
    required: false,
    type: Function
  },
  sections: {
    required: true,
    type: Array as PropType<SectionEdit[]>
  },
  stageDeleteAction: {
    default: () => {},
    required: false,
    type: Function
  },
  stageAddAction: {
    default: () => {},
    required: false,
    type: Function
  },
  stageUpdateAction: {
    default: () => {},
    required: false,
    type: Function
  },
  tableCaption: {
    default: 'Official sections in this course',
    required: false,
    type: String
  },
  unstageAction: {
    default: () => {},
    required: false,
    type: Function
  },
  updateSelected: {
    default: () => {},
    required: false,
    type: Function
  }
})

const contextStore = useContextStore()
const allSelected = ref(false)
const config = contextStore.config
const currentUser = contextStore.currentUser
const displayableSections = computed<SectionEdit[]>((): SectionEdit[] => {
  return filter(props.sections, s => props.rowDisplayLogic(props.mode, s))
})
const hasSectionScheduleData = ref(false)
const indeterminate = ref(false)
const meetingDaysPattern = /([A-Z]{2})/g
const sectionDisplayClass = ref({})
const sectionToUnlink = ref<SectionAndIndex | undefined>()
const selected = ref<number[]>([])
const showAreYouSureModal = ref(false)

watch(selected, (objects: number[]) => {
  if (!objects.length) {
    allSelected.value = false
    indeterminate.value = false
  } else if (objects.length === props.sections.length) {
    allSelected.value = true
    indeterminate.value = false
  } else {
    allSelected.value = false
    indeterminate.value = true
  }
  each(props.sections, section => {
    section.selected = includes(selected.value, section.id)
  })
  props.updateSelected()
})

onMounted(() => {
  selected.value = map(filter(props.sections, 'selected'), 'id')
  updateSectionDisplay()
  hasSectionScheduleData.value = !!find(displayableSections.value, s => get(s, 'schedules.recurring', []).length)
  contextStore.eventHub.on('sections-table-updated', updateSectionDisplay)
})

const describeSchedule = (schedule) => {
  const meetingDaysMap = {
    SU: 'Sundays',
    MO: 'Mondays',
    TU: 'Tuesdays',
    WE: 'Wednesdays',
    TH: 'Thursdays',
    FR: 'Fridays',
    SA: 'Saturdays'
  }
  const meetingDays = map(schedule.meetingDays.match(meetingDaysPattern), abbr => meetingDaysMap[abbr])
  const startTime = moment(schedule.meetingStartTime, 'HH:mm').format('LT')
  const endTime = moment(schedule.meetingEndTime, 'HH:mm').format('LT')
  return `${oxfordJoin(meetingDays)}, ${startTime} to ${endTime}`
}

const getNextFocusTarget = (
  section: SectionEdit,
  sectionIndex: number,
  totalStagedCount: number,
  action: string
) => {
  // Allow focus to toggle between Update and Undo Update buttons on the same row.
  if (action === 'update') {
    return `section-${section.id}-undo-update-btn`
  } else if (action === 'undo-update') {
    return `section-${section.id}-update-btn`
  }
  if (size(displayableSections.value) > 0) {
    // If any section rows remain, try to move focus to the next row that has a button.
    const nextFocusSection: SectionEdit | undefined = props.mode === 'currentStaging' ? get(displayableSections.value, sectionIndex) : find(displayableSections.value, s => s.stagedState, sectionIndex)
    if (showUpdateButton(nextFocusSection)) {
      return `section-${nextFocusSection.id}-update-btn`
    }
    if (nextFocusSection) {
      let nextAction
      if (props.mode === 'availableStaging' && nextFocusSection.stagedState === 'delete') {
        nextAction = 'undo-unlink'
      }
      if (nextFocusSection.stagedState === 'add') {
        nextAction = 'undo-link'
      }
      if (props.mode === 'currentStaging' && !nextFocusSection.stagedState) {
        nextAction = 'unlink'
      }
      if (document.getElementById(`section-${nextFocusSection.id}-${nextAction}-btn`)) {
        return `section-${nextFocusSection.id}-${nextAction}-btn`
      }
    }
  }
  // If we've reached the end of the staging area and there's a secondary save button, go there.
  if (props.mode === 'currentStaging' && totalStagedCount > 12) {
    return 'official-sections-secondary-save-btn'
  }
  // If no other buttons, move focus to the expansion panel button for this section's course.
  return `sections-course-${section.courseSlug}-btn`
}

const filterRecurring = (section: SectionEdit, key) => filter(section.schedules.recurring, key)

const noCurrentSections = () => {
  if (props.sections.length < 1) {
    return true
  }
  return !props.sections.some(section => {
    return (section.isCourseSection && section.stagedState !== 'delete') || (!section.isCourseSection && section.stagedState === 'add')
  })
}

const showUpdateButton = (section) => {
  return section && props.mode === 'currentStaging' && section.nameDiscrepancy && section.stagedState !== 'update'
}

const stageAdd = (section, index) => {
  const totalStagedCount = props.stageAddAction(section)
  putFocusNextTick(getNextFocusTarget(section, index, totalStagedCount, 'link'))
  contextStore.eventHub.emit('sections-table-updated')
}

const stageUpdate = (section: SectionEdit) => {
  props.stageUpdateAction(section)
  putFocusNextTick(`section-${section.id}-undo-update-btn`)
  contextStore.eventHub.emit('sections-table-updated')
}

const stageDeleteProceed = () => {
  if (sectionToUnlink.value) {
    const section = sectionToUnlink.value.section
    const index = sectionToUnlink.value.index
    showAreYouSureModal.value = false
    const totalStagedCount = props.stageDeleteAction(section)
    putFocusNextTick(getNextFocusTarget(section, index, totalStagedCount, 'unlink'))
    contextStore.eventHub.emit('sections-table-updated')
    sectionToUnlink.value = undefined
  }
}

const stageDeleteCancel = () => {
  showAreYouSureModal.value = false
  if (sectionToUnlink.value) {
    putFocusNextTick(`section-${sectionToUnlink.value.section.id}-unlink-btn`)
    sectionToUnlink.value = undefined
  }
}

const stageDeletePreCheck = (section: SectionEdit, index: number) => {
  sectionToUnlink.value = {index, section}
  const sectionsInstructedByMe = filter(displayableSections.value, s => map(s.instructors, 'uid').includes(currentUser.uid))
  if (sectionsInstructedByMe.length === 1 && sectionsInstructedByMe[0].id === section.id) {
    showAreYouSureModal.value = true
  } else {
    stageDeleteProceed()
  }
}

const toggleAll = () => {
  selected.value = allSelected.value ? map(props.sections, 'id').slice() : []
}

const updateSectionDisplay = () => {
  displayableSections.value.forEach(s => {
    sectionDisplayClass.value[s.id] = props.rowClassLogic(props.mode, s)
  })
}

const unstage = (section, index, action) => {
  const totalStagedCount = props.unstageAction(section)
  putFocusNextTick(getNextFocusTarget(section, index, totalStagedCount, action))
  contextStore.eventHub.emit('sections-table-updated')
}
</script>

<style scoped lang="scss">
@media screen and (min-width: 600px) {
  .sr-only-in-standard-viewport {
    display: none;
  }
  .td-checkbox {
    width: 5%;
  }
  .td-course-code {
    min-width: 100px;
    vertical-align: middle;
    width: 5%
  }
  .td-actions {
    height: 45px;
    min-width: 80px;
    padding-right: 10px;
    text-align: right !important;
    width: 10%
  }
  .td-section-id {
    min-width: 70px;
    vertical-align: middle;
    width: 10%
  }
  .td-instructors {
    min-width: 183px;
    vertical-align: middle;
    width: 15%
  }
  .td-section-name {
    min-width: 115px;
    vertical-align: middle;
    width: 15%
  }
  .td-meeting-location {
    min-width: 150px;
    vertical-align: middle;
    width: 15%
  }
  .td-schedule {
    min-width: 155px;
    vertical-align: middle;
    width: 15%
  }
  .td-shrink-to-fit {
    vertical-align: middle;
    width: 1%;
  }
  .responsive-justify-end {
    justify-content: flex-end !important;
  }
}
@media screen and (max-width: 600px) {
  table {
    border-collapse: collapse;
  }
  table thead {
    border: 0;
    clip: rect(0 0 0 0);
    height: 1px;
    margin: -1px;
    overflow: hidden;
    padding: 0;
    position: absolute;
    width: 1px;
  }
  table tr {
    border: 0;
    border-bottom: 1pt solid $color-container-grey-border;
    display: block;
    width: 100%;
  }
  table td {
    border: 0;
    display: block;
    padding: 3px 0;
    width: 100%;
  }
  table td::before {
    content: attr(data-label);
    float: left;
  }
  table tr:first-child {
    padding-top: 12px;
  }
  tr td:last-child {
    padding-bottom: 12px;
    padding-top: 8px;
  }
  .instructors {
    padding: 0 0 4px 8px;
  }
  .sr-only-in-standard-viewport {
    font-weight: bolder;
  }
  .td-actions {
    margin-left: -4px;
    margin-bottom: 8px;
    text-align: left !important;
  }
}
th {
  font-size: 14px;
  font-weight: bolder;
}
.border-top-zero {
  border-top: 0;
}
.button-undo-add {
  background-color: $color-orange-button-bg !important;
  border: $color-orange-button-border solid 1px !important;
  color: $color-white !important;
  &:hover, &:active, &:focus, &:link {
    background: $color-orange-button-bg-selected !important;
    border-color: $color-orange-button-border-selected !important;
  }
}
.button-undo-delete {
  background-color: $color-red-button-bg !important;
  border: $color-red-button-border solid 1px !important;
  color: $color-white !important;
  &:hover, &:active, &:focus, &:link {
    background: $color-red-button-bg-selected !important;
    border-color: $color-red-button-border-selected !important;
  }
}
.row-added td {
  background-color: $color-yellow-row-highlighted !important;
}
.row-deleted td {
  background-color: $color-red-row-highlighted !important;
}
.row-disabled td {
  color: $color-grey-disabled !important;
}
.section-in-use-icon {
  padding: 0 4px 2px 0;
}
</style>
