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
    <table id="template-sections-table">
      <thead>
        <tr>
          <th v-if="mode === 'createCourseForm'" class="pl-4 pr-0 td-checkbox">Action</th>
          <th class="td-course-code">Course Code</th>
          <th class="td-section-name">Section Name</th>
          <th class="td-section-id text-no-wrap">Section ID</th>
          <th :class="{'td-schedule': hasSectionScheduleData, 'td-shrink-to-fit': !hasSectionScheduleData}">
            Schedule
          </th>
          <th :class="{'td-meeting-location': hasSectionScheduleData, 'td-shrink-to-fit': !hasSectionScheduleData}">
            Location
          </th>
          <th class="td-instructors">Instructors</th>
          <th v-if="mode !== 'createCourseForm' && mode !== 'preview'" class="td-actions">
            <span v-if="mode !== 'preview'" class="mr-5">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody v-for="section in displayableSections" :key="section.id">
        <tr :id="`template-sections-table-row-${mode.toLowerCase()}-${section.id}`" :class="sectionDisplayClass[section.id]">
          <td v-if="mode === 'createCourseForm'" class="align-top td-checkbox pl-3 pr-0 py-0">
            <v-checkbox
              :id="`template-canvas-manage-sections-checkbox-${section.id}`"
              v-model="selected"
              :aria-checked="section.selected"
              :aria-label="`Checkbox for ${section.courseCode} ${section.name}`"
              class="ml-2"
              density="compact"
              hide-details
              name="section-section-id"
              :value="section.id"
            />
          </td>
          <td class="td-course-code text-no-wrap">
            {{ section.courseCode }}
          </td>
          <td class="td-section-name">
            <label
              v-if="mode === 'createCourseForm'"
              :for="`template-canvas-manage-sections-checkbox-${section.id}`"
            >
              {{ section.name }}
            </label>
            <span v-if="mode !== 'createCourseForm'">{{ section.name }}</span>
            <span v-if="mode === 'currentStaging' && section.nameDiscrepancy && section.stagedState !== 'update'" class="sr-only">
              The section name in bCourses no longer matches the Student Information System.
              Use the "Update" button to rename your bCourses section name to match SIS.
            </span>
          </td>
          <td class="td-section-id">{{ section.id }}</td>
          <td :class="{'td-schedule': hasSectionScheduleData, 'td-shrink-to-fit': !hasSectionScheduleData}">
            <div v-if="filterRecurring(section, 'schedule').length">
              <div
                v-for="(schedule, index) in uniqBy(filterRecurring(section, 'schedule'), 'schedule')"
                :key="index"
              >
                {{ schedule.schedule }}
              </div>
            </div>
            <span v-if="!filterRecurring(section, 'schedule').length">&mdash;</span>
          </td>
          <td :class="{'td-meeting-location': hasSectionScheduleData, 'td-shrink-to-fit': !hasSectionScheduleData}">
            <div v-if="filterRecurring(section, 'buildingName').length">
              <div
                v-for="(schedule, index) in filterRecurring(section, 'buildingName')"
                :key="index"
              >
                {{ schedule.buildingName }} {{ schedule.roomNumber }}
              </div>
            </div>
            <span v-if="!filterRecurring(section, 'buildingName').length">&mdash;</span>
          </td>
          <td class="td-instructors">
            <div v-if="filter(section.instructors, 'name').length">
              <div
                v-for="instructor in section.instructors"
                :key="instructor.uid"
              >
                {{ instructor.name }}
              </div>
            </div>
            <span v-if="!filter(section.instructors, 'name').length">&mdash;</span>
          </td>
          <td v-if="!['createCourseForm', 'preview'].includes(mode)" class="td-actions">
            <!-- Current Staging Actions -->
            <div v-if="mode === 'currentStaging' && section.isCourseSection" class="d-flex flex-nowrap justify-end">
              <v-btn
                v-if="section.nameDiscrepancy && section.stagedState !== 'update'"
                :id="`section-${section.id}-update-btn`"
                :aria-label="`Include '${section.courseCode} ${section.name}' in the list of sections to be updated`"
                class="ml-1"
                @click="stageUpdate(section)"
              >
                Update
              </v-btn>
              <v-btn
                v-if="section.stagedState === 'update'"
                :id="`section-${section.id}-undo-update-btn`"
                :aria-label="`Remove '${section.courseCode} ${section.name}' from list of sections to be updated from course site`"
                class="button-undo-delete ml-1"
                density="compact"
                @click="unstage(section)"
              >
                Undo Update
              </v-btn>
              <v-btn
                v-if="section.stagedState !== 'update'"
                :id="`section-${section.id}-unlink-btn`"
                :aria-label="`Include '${section.courseCode} ${section.name}' in the list of sections to be unlinked from course site`"
                class="ml-1"
                density="compact"
                @click="stageDelete(section)"
              >
                Unlink
              </v-btn>
            </div>
            <div v-if="mode === 'currentStaging' && !section.isCourseSection">
              <v-btn
                :id="`section-${section.id}-undo-unlink-btn`"
                class="button-undo-add ml-1"
                :aria-label="`Remove '${section.courseCode} ${section.name}' from list of sections to be linked to course site`"
                density="compact"
                @click="unstage(section)"
              >
                Undo Link
              </v-btn>
            </div>
            <!-- Available Staging Actions -->
            <div v-if="mode === 'availableStaging' && section.isCourseSection && section.stagedState === 'delete'">
              <v-btn
                :id="`section-${section.id}-undo-unlink-btn`"
                :aria-label="`Remove '${section.courseCode} ${section.name}' from list of sections to be unlinked from course site`"
                class="button-undo-delete ml-1"
                density="compact"
                @click="unstage(section)"
              >
                Undo Unlink
              </v-btn>
            </div>
            <div v-if="mode === 'availableStaging' && !section.isCourseSection && section.stagedState === 'add'">
              Linked <span class="sr-only">to pending list of new sections</span>
            </div>
            <div v-if="mode === 'availableStaging' && !section.isCourseSection && !section.stagedState">
              <v-btn
                :id="`section-${section.id}-link-btn`"
                :aria-label="`Include '${section.courseCode} ${section.name}' in the list of sections to be linked to course site`"
                class="ml-1"
                :class="{'button-undo-add': section.stagedState === 'add'}"
                @click="stageAdd(section)"
              >
                Link
              </v-btn>
            </div>
          </td>
        </tr>
        <tr
          v-if="mode === 'currentStaging' && section.nameDiscrepancy && section.stagedState !== 'update'"
          aria-hidden="true"
          :class="sectionDisplayClass[section.id]"
        >
          <td></td>
          <td colspan="6">
            <div>
              <v-icon class="sited-icon mr-1" :icon="mdiInformationVariantCircle" />
              The section name in bCourses no longer matches the Student Information System.
              Use the "Update" button to rename your bCourses section name to match SIS.
            </div>
          </td>
        </tr>
        <tr
          v-if="!['currentStaging', 'preview'].includes(mode) && size(section.canvasSites)"
          :class="sectionDisplayClass[section.id]"
        >
          <td class="border-top-zero pa-0"></td>
          <td colspan="7" class="border-top-zero pb-4 pt-0">
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
                <OutboundLink :href="`${config.canvasApiUrl}/courses/${section.canvasSites[0].canvasSiteId}`">{{ section.canvasSites[0].name }}</OutboundLink>
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
                  <li><OutboundLink :href="`${config.canvasApiUrl}/courses/${canvasSite.canvasSiteId}`">{{ canvasSite.name }}</OutboundLink></li>
                </ul>
              </div>
            </div>
          </td>
        </tr>
      </tbody>
      <tbody v-if="mode === 'preview' && sections.length < 1">
        <tr>
          <td colspan="7">There are no currently maintained official sections in this course site.</td>
        </tr>
      </tbody>
      <tbody v-if="mode === 'currentStaging' && noCurrentSections()">
        <tr>
          <td colspan="7">No official sections will remain in course site</td>
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

export default {
  name: 'CourseSectionsTable',
  components: {OutboundLink},
  mixins: [Context],
  props: {
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
    displayableSections: [],
    hasSectionScheduleData: false,
    indeterminate: false,
    sectionDisplayClass: {},
    selected: undefined
  }),
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
    size,
    stageAdd(section) {
      this.stageAddAction(section)
      this.eventHub.emit('sections-table-updated')
    },
    stageUpdate(section) {
      this.stageUpdateAction(section)
      this.eventHub.emit('sections-table-updated')
    },
    stageDelete(section) {
      this.stageDeleteAction(section)
      this.eventHub.emit('sections-table-updated')
    },
    toggleAll() {
      this.selected = this.allSelected ? map(this.sections, 'id').slice() : []
    },
    updateSectionDisplay() {
      this.displayableSections = filter(this.sections, s => this.rowDisplayLogic(this.mode, s))
      this.displayableSections.forEach(s => {
        this.sectionDisplayClass[s.id] = this.rowClassLogic(this.mode, s)
      })
    },
    unstage(section) {
      this.unstageAction(section)
      this.eventHub.emit('sections-table-updated')
    }
  }
}
</script>

<style scoped lang="scss">
td, th {
  padding: 10px;
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
