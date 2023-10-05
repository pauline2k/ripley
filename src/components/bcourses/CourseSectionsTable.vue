<template>
  <div class="bg-white mb-1 mt-4">
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
          <th v-if="mode === 'createCourseForm'" class="cell-checkbox pl-4 pr-0">Action</th>
          <th class="cell-course-code">Course Code</th>
          <th class="cell-section-label">Section Name</th>
          <th class="cell-section-id">Section ID</th>
          <th class="cell-section-timestamps d-none d-sm-none d-md-table-cell">Schedule</th>
          <th class="cell-section-locations d-none d-sm-none d-md-table-cell">Location</th>
          <th class="cell-section-instructors d-none d-sm-none d-lg-table-cell">Instructors</th>
          <th v-if="mode !== 'createCourseForm' && mode !== 'preview'" class="cell-section-action-option">
            <span v-if="mode !== 'preview'" class="mr-5">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody v-for="section in displayableSections" :key="section.id">
        <tr :id="`template-sections-table-row-${mode.toLowerCase()}-${section.id}`" :class="sectionDisplayClass[section.id]">
          <td v-if="mode === 'createCourseForm'" class="align-top cell-checkbox pl-3 pr-0 py-0">
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
          <td class="cell-course-code">
            {{ section.courseCode }}
          </td>
          <td class="cell-section-label">
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
          <td class="cell-section-id">{{ section.id }}</td>
          <td class="cell-section-timestamps d-none d-sm-none d-md-table-cell">
            <div v-for="(schedule, index) in section.schedules.recurring" :key="index">{{ schedule.schedule }}</div>
            <span v-if="!section.schedules.recurring.length">&mdash;</span>
          </td>
          <td class="cell-section-locations d-none d-sm-none d-md-table-cell">
            <div v-for="(schedule, index) in section.schedules.recurring" :key="index">{{ schedule.buildingName }} {{ schedule.roomNumber }}</div>
            <span v-if="!section.schedules.recurring.length">&mdash;</span>
          </td>
          <td class="cell-section-instructors d-none d-sm-none d-lg-table-cell">
            <div v-for="instructor in section.instructors" :key="instructor.uid">{{ instructor.name }}</div>
          </td>
          <td v-if="!['createCourseForm', 'preview'].includes(mode)" class="cell-section-action-option">
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
              <v-icon icon="mdi-info-circle" class="sited-icon mr-1" />
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
          <td colspan="6" class="border-top-zero pb-4 pt-0">
            <div v-if="section.canvasSites.length === 1">
              <v-icon
                color="error"
                icon="mdi-alert"
                size="medium"
              />
              This section is already in use by
              <OutboundLink :href="`${config.canvasApiUrl}/courses/${section.canvasSites[0].canvasSiteId}`">{{ section.canvasSites[0].name }}</OutboundLink>
            </div>
            <div v-if="section.canvasSites.length > 1">
              <div>
                <v-icon
                  color="error"
                  icon="mdi-alert"
                  size="medium"
                />
                This section is already in use by:
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

<script>
import Context from '@/mixins/Context'
import OutboundLink from '@/components/utils/OutboundLink'
import {each, filter, includes, map, size} from 'lodash'

export default {
  name: 'CourseSectionsTable',
  mixins: [Context],
  components: {OutboundLink},
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
  data: () => ({
    selected: undefined,
    allSelected: false,
    indeterminate: false,
    displayableSections: [],
    sectionDisplayClass: {}
  }),
  created() {
    this.selected = map(filter(this.sections, 'selected'), 'id')
    this.updateSectionDisplay()
    this.eventHub.on('sections-table-updated', this.updateSectionDisplay)
  },
  methods: {
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
.button {
  font-size: 13px !important;
  height: unset;
  padding: 2px 8px !important;
  white-space: nowrap;
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
.cell-checkbox {
  width: 5%;
}
.cell-course-code {
  min-width: 100px;
  width: 5%
}
.cell-section-action-option {
  height: 45px;
  min-width: 80px;
  padding-right: 10px;
  text-align: right !important;
  width: 10%
}
.cell-section-id {
  min-width: 70px;
  width: 10%
}
.cell-section-instructors {
  min-width: 183px;
  width: 15%
}
.cell-section-label {
  min-width: 115px;
  width: 15%
}
.cell-section-locations {
  min-width: 150px;
  width: 15%
}
.cell-section-timestamps {
  min-width: 155px;
  width: 15%
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
</style>
