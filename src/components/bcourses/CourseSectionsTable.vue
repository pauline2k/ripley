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
          <th class="td-course-code" scope="col">Course Code</th>
          <th class="td-section-name" scope="col">Section Name</th>
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
              :aria-label="`${section.selected ? 'Deselect' : 'Select'} ${section.courseCode} ${section.name}`"
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
            <span class="sr-only">Instructors, </span>
            <template v-if="filter(section.instructors, 'name').length">
              <span
                v-for="instructor in section.instructors"
                :key="instructor.uid"
                class="d-block"
              >
                {{ instructor.name }} <span class="sr-only">,</span>
              </span>
            </template>
            <template v-else>
              <span aria-hidden="true">&mdash;</span>
              <span class="sr-only">blank</span>
            </template>
          </td>
          <td v-if="!['createCourseForm', 'preview'].includes(mode)" :id="`${id}-${section.id}-actions`" class="td-actions">
            <!-- Current Staging Actions -->
            <div v-if="mode === 'currentStaging' && section.isCourseSection" class="d-flex flex-nowrap justify-end">
              <v-btn
                v-if="section.nameDiscrepancy && section.stagedState !== 'update'"
                :id="`section-${section.id}-update-btn`"
                :aria-label="`Update '${section.courseCode} ${section.name}' section name`"
                class="ml-1"
                density="compact"
                @click="stageUpdate(section)"
              >
                Update
              </v-btn>
              <v-btn
                v-if="section.stagedState === 'update'"
                :id="`section-${section.id}-undo-update-btn`"
                :aria-label="`Undo update '${section.courseCode} ${section.name}' section name`"
                class="button-undo-delete ml-1"
                density="compact"
                @click="unstage(section, sectionIndex, 'undo-update')"
              >
                Undo Update
              </v-btn>
              <v-btn
                v-if="section.stagedState !== 'update'"
                :id="`section-${section.id}-unlink-btn`"
                :aria-label="`Unlink '${section.courseCode} ${section.name}' from the course site`"
                class="ml-1"
                density="compact"
                @click="stageDelete(section, sectionIndex)"
              >
                Unlink
              </v-btn>
            </div>
            <div v-if="mode === 'currentStaging' && !section.isCourseSection">
              <v-btn
                :id="`section-${section.id}-undo-link-btn`"
                class="button-undo-add ml-1"
                :aria-label="`Undo link '${section.courseCode} ${section.name}' to the course site`"
                density="compact"
                @click="unstage(section, sectionIndex, 'undo-link')"
              >
                Undo Link
              </v-btn>
            </div>
            <!-- Available Staging Actions -->
            <div v-if="mode === 'availableStaging' && section.isCourseSection && section.stagedState === 'delete'">
              <v-btn
                :id="`section-${section.id}-undo-unlink-btn`"
                :aria-label="`Undo unlink '${section.courseCode} ${section.name}' from the course site`"
                class="button-undo-delete ml-1"
                density="compact"
                @click="unstage(section, sectionIndex, 'undo-unlink')"
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
                @click="stageAdd(section, sectionIndex)"
              >
                Link
              </v-btn>
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
          <td class="border-none"></td>
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
          <td class="border-top-zero pa-0"></td>
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
              <div>
                bCourses site
                <OutboundLink :id="`${id}-${section.id}-warning-link`" :href="`${config.canvasApiUrl}/courses/${section.canvasSites[0].canvasSiteId}`">{{ section.canvasSites[0].name }}</OutboundLink>
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
                <div>
                  The following bCourses sites include this section.
                </div>
              </div>
              <div class="ml-6 pt-1">
                <ul v-for="(canvasSite, index) in section.canvasSites" :key="index" class="sites-container">
                  <li><OutboundLink :id="`${id}-${section.id}-warning-link`" :href="`${config.canvasApiUrl}/courses/${canvasSite.canvasSiteId}`">{{ canvasSite.name }}</OutboundLink></li>
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
  </div>
</template>

<script setup>
import {mdiAlert, mdiInformationVariantCircle} from '@mdi/js'
import {uniqBy} from 'lodash'
</script>

<script>
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import {each, filter, find, get, includes, map, size} from 'lodash'
import {oxfordJoin, putFocusNextTick} from '@/utils'

const _meetingDaysPattern = /([A-Z]{2})/g

export default {
  name: 'CourseSectionsTable',
  components: {OutboundLink},
  mixins: [Context],
  props: {
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
      type: Array
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
  },
  data: () => ({
    allSelected: false,
    hasSectionScheduleData: false,
    indeterminate: false,
    sectionDisplayClass: {},
    selected: undefined
  }),
  computed: {
    displayableSections() {
      return filter(this.sections, s => this.rowDisplayLogic(this.mode, s))
    }
  },
  watch: {
    selected(objects) {
      if (!objects.length) {
        this.allSelected = false
        this.indeterminate = false
      } else if (objects.length === this.sections.length) {
        this.allSelected = true
        this.indeterminate = false
      } else {
        this.allSelected = false
        this.indeterminate = true
      }
      each(this.sections, section => {
        section.selected = includes(this.selected, section.id)
      })
      this.updateSelected()
    }
  },
  created() {
    this.selected = map(filter(this.sections, 'selected'), 'id')
    this.updateSectionDisplay()
    this.hasSectionScheduleData = !!find(this.displayableSections, s => get(s, 'schedules.recurring', []).length)
    this.eventHub.on('sections-table-updated', this.updateSectionDisplay)
  },
  methods: {
    describeSchedule(schedule) {
      const meetingDaysMap = {
        'SU': 'Sundays',
        'MO': 'Mondays',
        'TU': 'Tuesdays',
        'WE': 'Wednesdays',
        'TH': 'Thursdays',
        'FR': 'Fridays',
        'SA': 'Saturdays'
      }
      const meetingDays = map(schedule.meetingDays.match(_meetingDaysPattern), abbr => meetingDaysMap[abbr])
      const startTime = this.$moment(schedule.meetingStartTime, 'HH:mm').format('LT')
      const endTime = this.$moment(schedule.meetingEndTime, 'HH:mm').format('LT')
      return `${oxfordJoin(meetingDays)}, ${startTime} to ${endTime}`
    },
    getNextFocusTarget(section, sectionIndex, totalStagedCount, action) {
      // Allow focus to toggle between Update and Undo Update buttons on the same row.
      if (action === 'update') {
        return `section-${section.id}-undo-update-btn`
      } else if (action === 'undo-update') {
        return `section-${section.id}-update-btn`
      }
      if (size(this.displayableSections) > 0) {
        // If any section rows remain, try to move focus to the next row that has a button.
        const nextFocusSection = this.mode === 'currentStaging' ? get(this.displayableSections, sectionIndex) : find(this.displayableSections, s => s.stagedState, sectionIndex)
        if (this.showUpdateButton(nextFocusSection)) {
          return `section-${nextFocusSection.id}-update-btn`
        }
        if (nextFocusSection) {
          let nextAction
          if (this.mode === 'availableStaging' && nextFocusSection.stagedState === 'delete') {
            nextAction = 'undo-unlink'
          }
          if (nextFocusSection.stagedState === 'add') {
            nextAction = 'undo-link'
          }
          if (this.mode === 'currentStaging' && !nextFocusSection.stagedState) {
            nextAction = 'unlink'
          }
          if (document.getElementById(`section-${nextFocusSection.id}-${nextAction}-btn`)) {
            return `section-${nextFocusSection.id}-${nextAction}-btn`
          }
        }
      }
      // If we've reached the end of the staging area and there's a secondary save button, go there.
      if (this.mode === 'currentStaging' && totalStagedCount > 12) {
        return 'official-sections-secondary-save-btn'
      }
      // If no other buttons, move focus to the expansion panel button for this section's course.
      return `sections-course-${section.courseSlug}-btn`
    },
    filter,
    filterRecurring(section, key) {
      return filter(section.schedules.recurring, key)
    },
    noCurrentSections() {
      if (this.sections.length < 1) {
        return true
      }
      return !this.sections.some(section => {
        return (section.isCourseSection && section.stagedState !== 'delete') || (!section.isCourseSection && section.stagedState === 'add')
      })
    },
    showUpdateButton(section) {
      return section && this.mode === 'currentStaging' && section.nameDiscrepancy && section.stagedState !== 'update'
    },
    size,
    stageAdd(section, index) {
      const totalStagedCount = this.stageAddAction(section)
      putFocusNextTick(this.getNextFocusTarget(section, index, totalStagedCount, 'link'))
      this.eventHub.emit('sections-table-updated')
    },
    stageUpdate(section) {
      this.stageUpdateAction(section)
      putFocusNextTick(`section-${section.id}-undo-update-btn`)
      this.eventHub.emit('sections-table-updated')
    },
    stageDelete(section, index) {
      const totalStagedCount = this.stageDeleteAction(section)
      putFocusNextTick(this.getNextFocusTarget(section, index, totalStagedCount, 'unlink'))
      this.eventHub.emit('sections-table-updated')
    },
    toggleAll() {
      this.selected = this.allSelected ? map(this.sections, 'id').slice() : []
    },
    updateSectionDisplay() {
      this.displayableSections.forEach(s => {
        this.sectionDisplayClass[s.id] = this.rowClassLogic(this.mode, s)
      })
    },
    unstage(section, index, action) {
      const totalStagedCount = this.unstageAction(section)
      putFocusNextTick(this.getNextFocusTarget(section, index, totalStagedCount, action))
      this.eventHub.emit('sections-table-updated')
    }
  }
}
</script>

<style scoped lang="scss">
td, th {
  padding: 10px;
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
.td-checkbox {
  width: 5%;
}
.td-course-code {
  min-width: 100px;
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
  width: 10%
}
.td-instructors {
  min-width: 183px;
  width: 15%
}
.td-section-name {
  min-width: 115px;
  width: 15%
}
.td-meeting-location {
  min-width: 150px;
  width: 15%
}
.td-schedule {
  min-width: 155px;
  width: 15%
}
.td-shrink-to-fit {
  width: 1%;
  white-space: nowrap;
}
</style>
