<template>
  <div>
    <h2 class="sr-only">Administrator Options</h2>
    <div class="text-subtitle-1">Choose courses by:</div>
    <v-radio-group
      v-model="adminModeModel"
      color="primary"
      density="compact"
      :disabled="isFetching"
      hide-details
    >
      <v-radio id="radio-btn-mode-act-as" value="actAs">
        <template #label>
          <div class="font-weight-medium pl-1 text-subtitle-1">Instructor UID</div>
        </template>
      </v-radio>
      <v-radio id="radio-btn-mode-section-id" value="bySectionId">
        <template #label>
          <div class="font-weight-medium pl-1 text-subtitle-1">Section IDs</div>
        </template>
      </v-radio>
    </v-radio-group>
    <div v-if="adminMode === 'actAs'" class="pt-5">
      <h3 class="sr-only">Load Sections By Instructor UID</h3>
      <div class="align-center d-flex pb-3">
        <div class="pr-3">
          <label for="instructor-uid" class="sr-only">Instructor UID</label>
          <v-text-field
            id="instructor-uid"
            v-model="uid"
            class="instructor-uid-text-field"
            density="comfortable"
            :disabled="isFetching"
            :error="isInvalidUID"
            hide-details
            maxlength="16"
            placeholder="Instructor UID"
            variant="outlined"
            @keydown.enter="submit"
          />
        </div>
        <div>
          <v-btn
            id="sections-by-uid-button"
            aria-controls="page-create-course-site-steps-container"
            aria-label="Load official sections for instructor"
            color="primary"
            :disabled="isFetching || !trim(uid) || isInvalidUID"
            size="large"
            @click="submit"
          >
            <span v-if="isFetching">
              <v-progress-circular
                class="mr-1"
                indeterminate
                size="18"
              />
              Fetching...
            </span>
            <span v-if="!isFetching">As instructor</span>
          </v-btn>
        </div>
      </div>
    </div>
    <div v-if="adminMode === 'bySectionId'" class="py-5">
      <h3 class="sr-only">Load Sections by ID</h3>
      <div v-if="size(adminTerms)">
        <div class="d-flex pb-3">
          <v-btn-toggle
            v-model="slug"
            class="term-btn-toggle"
            color="primary"
          >
            <v-btn
              v-for="(term, index) in adminTerms"
              :id="`term${index}`"
              :key="index"
              :disabled="isFetching"
              :value="term.slug"
            >
              {{ term.name }}
            </v-btn>
          </v-btn-toggle>
        </div>
        <div class="pb-3">
          <label
            for="page-create-course-site-section-id-list"
            class="sr-only"
          >
            Provide Section ID List Separated by Commas or Spaces
          </label>
          <v-textarea
            id="page-create-course-site-section-id-list"
            v-model="sectionIds"
            auto-grow
            clearable
            density="comfortable"
            :disabled="isFetching"
            hide-details
            placeholder="Paste your list of Section IDs here, separated by commas or spaces"
            rows="2"
          />
        </div>
        <v-btn
          id="sections-by-ids-button"
          aria-controls="page-create-course-site-steps-container"
          color="primary"
          :disabled="!trim(sectionIds) || isFetching"
          @click="submit"
        >
          <span v-if="isFetching">
            <v-progress-circular
              class="mr-1"
              indeterminate
              size="18"
            />
            Fetching...
          </span>
          <span v-if="!isFetching">Review matching Section IDs</span>
        </v-btn>
      </div>
    </div>
    <div
      v-if="error"
      aria-live="polite"
      class="has-error pl-2 pt-2"
      role="alert"
    >
      {{ error }}
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {find, partition, size, split, trim} from 'lodash'
import {putFocusNextTick} from '@/utils'

export default {
  name: 'CreateCourseSiteHeader',
  mixins: [Context],
  watch: {
    sectionIds() {
      this.error = null
    },
    uid() {
      this.error = null
    }
  },
  props: {
    adminMode: {
      required: true,
      type: String
    },
    adminTerms: {
      default: undefined,
      required: false,
      type: Array
    },
    currentAdminTerm: {
      required: true,
      type: String
    },
    fetchFeed: {
      required: true,
      type: Function
    },
    isFetching: {
      required: true,
      type: Boolean
    },
    setAdminActingAs: {
      required: true,
      type: Function
    },
    setAdminBySectionIds: {
      required: true,
      type: Function
    },
    setAdminMode: {
      required: true,
      type: Function
    },
    showMaintenanceNotice: {
      required: true,
      type: Boolean
    },
    switchAdminTerm: {
      required: true,
      type: Function
    }
  },
  computed: {
    adminModeModel: {
      get() {
        return this.adminMode
      },
      set(mode) {
        this.error = undefined
        this.sectionIds = ''
        this.uid = undefined
        this.setAdminMode(mode)
        if (mode === 'bySectionId') {
          this.$announcer.polite('Input mode switched to section ID')
          putFocusNextTick('load-sections-by-id')
        } else {
          this.$announcer.polite(`Input mode switched to ${mode === 'bySectionId' ? 'section ID' : 'UID'}`)
          putFocusNextTick(mode === 'bySectionId' ? 'load-sections-by-id' : 'instructor-uid')
        }
      }
    },
    isInvalidUID() {
      return !!this.trim(this.uid) && !this.uid.match(/^\d+$/)
    },
    slug: {
      get() {
        return this.currentAdminTerm
      },
      set(slug) {
        const term = find(this.adminTerms, ['slug', slug])
        this.switchAdminTerm(term)
      }
    }
  },
  data: () => ({
    error: undefined,
    sectionIds: '',
    uid: undefined
  }),
  methods: {
    size,
    submit() {
      if (!this.isFetching) {
        if (this.adminMode === 'bySectionId' && trim(this.sectionIds)) {
          const trimmed = trim(this.sectionIds)
          const sectionIds = split(trimmed, /[,\r\n\t ]+/)
          const notNumeric = partition(sectionIds, sectionId => /^\d+$/.test(trim(sectionId)))[1]
          if (notNumeric.length) {
            this.error = 'Section IDs must be numeric.'
            putFocusNextTick('page-create-course-site-section-id-list')
          } else {
            this.setAdminBySectionIds(sectionIds)
            this.fetchFeed()
          }
        } else if (this.adminMode === 'actAs' && trim(this.uid) && !this.isInvalidUID) {
          const trimmed = trim(this.uid)
          if (/^\d+$/.test(trimmed)) {
            this.setAdminActingAs(trimmed)
            this.fetchFeed()
          } else {
            this.error = 'UID must be numeric.'
            putFocusNextTick('instructor-uid')
          }
        }
      }
    },
    trim
  }
}
</script>

<style scoped lang="scss">
.instructor-uid-text-field {
  width: 208px;
}
.has-error {
  color: $color-alert-error-foreground;
  font-size: 14px;
  font-weight: bolder;
}
.term-btn-toggle {
  border-width: 1px;
}
</style>
