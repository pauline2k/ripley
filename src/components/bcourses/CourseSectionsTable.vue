<template>
  <div class="template-sections-table-container">
    <div v-if="mode === 'createCourseForm' && sections.length > 1" class="d-flex pl-2">
      <v-checkbox
        :id="`select-all-toggle-${sections[0].ccn}`"
        v-model="allSelected"
        class="my-2"
        :indeterminate="indeterminate"
        @change="toggleAll"
      >
        <div class="text-secondary">
          Select {{ allSelected ? 'None' : 'All' }}
          <span class="sr-only">of the course sections</span>
        </div>
      </v-checkbox>
    </div>
    <table id="template-sections-table" class="template-sections-table bg-white">
      <thead class="visuallyhidden">
        <tr>
          <th v-if="mode === 'createCourseForm'">Action</th>
          <th>Course Code</th>
          <th>Section Label</th>
          <th>Course Control Number</th>
          <th>Schedule</th>
          <th>Location</th>
          <th>Instructors</th>
          <th v-if="mode !== 'createCourseForm' && mode !== 'preview'">
            <span v-if="mode !== 'preview'">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody v-for="section in displayableSections" :key="section.ccn">
        <tr :id="`template-sections-table-row-${mode.toLowerCase()}-${section.ccn}`" :class="sectionDisplayClass[section.ccn]">
          <td v-if="mode === 'createCourseForm'" class="align-top template-sections-table-cell-checkbox pl-2">
            <v-checkbox
              :id="`template-canvas-manage-sections-checkbox-${section.ccn}`"
              v-model="selected"
              :aria-checked="section.selected"
              :aria-label="`Checkbox for ${section.courseCode} ${section.section_label}`"
              class="ml-2"
              name="section-ccn"
              size="sm"
              :value="section.ccn"
            />
          </td>
          <td class="template-sections-table-cell-course-code">
            {{ section.courseCode }}
          </td>
          <td class="template-sections-table-cell-section-label">
            <label
              v-if="mode === 'createCourseForm'"
              class="template-sections-table-cell-section-label-label"
              :for="`template-canvas-manage-sections-checkbox-${section.ccn}`"
            >
              {{ section.section_label }}
            </label>
            <span v-if="mode !== 'createCourseForm'">{{ section.section_label }}</span>
            <span v-if="mode === 'currentStaging' && section.nameDiscrepancy && section.stagedState !== 'update'" class="sr-only">
              The section name in bCourses no longer matches the Student Information System.
              Use the "Update" button to rename your bCourses section name to match SIS.
            </span>
          </td>
          <td class="template-sections-table-cell-section-ccn">{{ section.ccn }}</td>
          <td class="template-sections-table-cell-section-timestamps d-none d-sm-none d-md-table-cell">
            <div v-for="(schedule, index) in section.schedules.recurring" :key="index">{{ schedule.schedule }}</div>
          </td>
          <td class="template-sections-table-cell-section-locations d-none d-sm-none d-md-table-cell">
            <div v-for="(schedule, index) in section.schedules.recurring" :key="index">{{ schedule.buildingName }} {{ schedule.roomNumber }}</div>
          </td>
          <td class="template-sections-table-cell-section-instructors d-none d-sm-none d-lg-table-cell">
            <div v-for="instructor in section.instructors" :key="instructor.uid">{{ instructor.name }}</div>
          </td>
          <td v-if="mode !== 'createCourseForm' && mode !== 'preview'" class="template-sections-table-cell-section-action-option">
            <!-- Current Staging Actions -->
            <div v-if="mode === 'currentStaging' && section.isCourseSection">
              <button
                v-if="section.nameDiscrepancy && section.stagedState !== 'update'"
                :aria-label="`Include '${section.courseCode} ${section.section_label}' in the list of sections to be updated`"
                class="canvas-button template-sections-table-button canvas-no-decoration"
                @click="stageUpdate(section)"
              >
                Update
              </button>
              <button
                v-if="section.stagedState === 'update'"
                :aria-label="`Remove '${section.courseCode} ${section.section_label}' from list of sections to be updated from course site`"
                class="canvas-button template-sections-table-button template-sections-table-button-undo-delete canvas-no-decoration"
                @click="unstage(section)"
              >
                Undo Update
              </button>
              <button
                v-if="section.stagedState !== 'update'"
                :aria-label="`Include '${section.courseCode} ${section.section_label}' in the list of sections to be unlinked from course site`"
                class="canvas-button template-sections-table-button canvas-no-decoration"
                @click="stageDelete(section)"
              >
                Unlink
              </button>
            </div>

            <div v-if="mode === 'currentStaging' && !section.isCourseSection">
              <button
                class="canvas-button template-sections-table-button template-sections-table-button-undo-add canvas-no-decoration"
                :aria-label="`Remove '${section.courseCode} ${section.section_label}' from list of sections to be linked to course site`"
                @click="unstage(section)"
              >
                Undo Link
              </button>
            </div>

            <!-- Available Staging Actions -->
            <div v-if="mode === 'availableStaging' && section.isCourseSection && section.stagedState === 'delete'">
              <button
                class="canvas-button template-sections-table-button template-sections-table-button-undo-delete canvas-no-decoration"
                :aria-label="`Remove '${section.courseCode} ${section.section_label}' from list of sections to be unlinked from course site`"
                @click="unstage(section)"
              >
                Undo Unlink
              </button>
            </div>

            <div v-if="mode === 'availableStaging' && !section.isCourseSection && section.stagedState === 'add'">
              Linked <span class="visuallyhidden">to pending list of new sections</span>
            </div>

            <div v-if="mode === 'availableStaging' && !section.isCourseSection && section.stagedState === null">
              <button
                class="canvas-button canvas-button-primary template-sections-table-button canvas-no-decoration"
                :class="{'template-sections-table-button-undo-add': section.stagedState === 'add'}"
                :aria-label="`Include '${section.courseCode} ${section.section_label}' in the list of sections to be linked to course site`"
                @click="stageAdd(section)"
              >
                Link
              </button>
            </div>
          </td>
        </tr>
        <tr
          v-if="mode === 'currentStaging' && section.nameDiscrepancy && section.stagedState !== 'update'"
          aria-hidden="true"
          :class="sectionDisplayClass[section.ccn]"
        >
          <td colspan="7" class="template-sections-table-sites-cell">
            <div class="template-sections-table-sites-container">
              <v-icon icon="mdi-info-circle" class="template-sections-table-sited-icon mr-1" />
              The section name in bCourses no longer matches the Student Information System.
              Use the "Update" button to rename your bCourses section name to match SIS.
            </div>
          </td>
        </tr>
        <tr
          v-if="(mode !== 'preview' && mode !== 'currentStaging' && section.sites)"
          :class="sectionDisplayClass[section.ccn]"
        >
          <td colspan="7" class="template-sections-table-sites-cell">
            <div v-for="(site, index) in section.sites" :key="index" class="template-sections-table-sites-container">
              <v-icon icon="mdi-info-circle" class="template-sections-table-sited-icon mr-1" size="sm" />
              This section is already in use by <OutboundLink :href="site.site_url">{{ site.name }}</OutboundLink>
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
      this.$_.each(this.sections, section => {
        section.selected = this.$_.includes(this.selected, section.ccn)
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
    this.selected = this.$_.map(this.$_.filter(this.sections, 'selected'), 'ccn')
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
    toggleAll(checked) {
      this.selected = checked ? this.$_.map(this.sections, 'ccn').slice() : []
    },
    updateSectionDisplay() {
      this.displayableSections = this.$_.filter(this.sections, s => this.rowDisplayLogic(this.mode, s))
      this.displayableSections.forEach(s => {
        this.sectionDisplayClass[s.ccn] = this.rowClassLogic(this.mode, s)
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
td {
  padding: 10px;
}
.template-sections-table {
  border: 1px solid $color-container-grey-border;
  border-collapse: separate;
  border-radius: 3px;
  border-spacing: 0;
  margin: 0;
  width: 100%;

  // disable alternating row color
  tr:nth-of-type(even) {
    background: inherit;
  }

  tbody tr:last-child td {
    border-bottom: $color-item-group-item-border solid 1px;
    vertical-align: top;
  }

  tbody:last-child tr:last-child td {
    border-bottom: 0;
    vertical-align: top;
  }
}
.template-sections-table-cell-checkbox {
  width: 30px;
}
.template-sections-table-row-disabled td {
  color: $color-grey-disabled;
}
.template-sections-table-row-added td {
  background-color: $color-yellow-row-highlighted;
}
.template-sections-table-row-deleted td {
  background-color: $color-red-row-highlighted;
}
.template-sections-table-cell-section-action-option {
  height: 45px;
  text-align: right;
}
.template-sections-table-button {
  font-size: 12px;
  margin: 0;
  padding: 2px 8px;
  white-space: nowrap;
}
.template-sections-table-button-undo-add {
  background-color: $color-orange-button-bg;
  border: $color-orange-button-border solid 1px;
  color: $color-white;
  &:hover, &:active, &:focus, &:link {
    background: $color-orange-button-bg-selected;
    border-color: $color-orange-button-border-selected;
  }
}
.template-sections-table-button-undo-delete {
  background-color: $color-red-button-bg;
  border: $color-red-button-border solid 1px;
  color: $color-white;
  &:hover, &:active, &:focus, &:link {
    background: $color-red-button-bg-selected;
    border-color: $color-red-button-border-selected;
  }
}
.template-sections-table-cell-course-code {
  font-size: 13px;
  width: 115px;
}
.template-sections-table-cell-section-ccn {
  width: 70px;
}
.template-sections-table-cell-section-timestamps {
  width: 155px;
}
.template-sections-table-cell-section-locations {
  width: 150px;
}
.template-sections-table-cell-section-instructors {
  width: 183px;
}
.template-sections-table-cell-section-label-label {
  cursor: pointer;
  font-size: 13px;
  margin: 0;
  text-align: left;
}
.template-sections-table-sited-icon {
  color: $color-help-link-blue;
}
.template-sections-table-sites-cell {
  padding: 0 14px;
}
.template-sections-table-sites-container {
  margin-bottom: 5px;
}
</style>
