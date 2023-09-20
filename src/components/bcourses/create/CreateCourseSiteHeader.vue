<template>
  <div>
    <h2 class="sr-only">Administrator Options</h2>
    <v-btn
      id="toggle-admin-mode-button"
      color="primary"
      :disabled="isFetching"
      @click="setMode(adminMode === 'actAs' ? 'bySectionId' : 'actAs')"
    >
      Switch to {{ adminMode === 'actAs' ? 'Section ID input' : 'acting as instructor' }}
    </v-btn>
    <div v-if="adminMode === 'actAs'" class="py-5">
      <h3 class="sr-only">Load Sections By Instructor UID</h3>
      <div class="pb-5">
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
          role="search"
          variant="outlined"
        />
      </div>
      <v-btn
        id="sections-by-uid-button"
        aria-controls="page-create-course-site-steps-container"
        aria-label="Load official sections for instructor"
        color="primary"
        :disabled="isFetching || !trim(uid) || isInvalidUID"
        @click="submit"
      >
        As instructor
      </v-btn>
    </div>
    <div v-if="adminMode === 'bySectionId'" class="py-5">
      <h3 class="sr-only">Load Sections by ID</h3>
      <div v-if="size(adminTerms)">
        <div class="d-flex pb-5">
          <div
            v-for="(term, index) in adminTerms"
            :key="index"
            class="pr-2"
          >
            <v-btn
              :id="`term${index}`"
              name="adminTerm"
              :aria-selected="currentAdminTerm === term.slug"
              :color="currentAdminTerm === term.slug ? 'primary' : ''"
              :disabled="isFetching"
              role="tab"
              @click="switchAdminTerm(term)"
              @keyup.enter="switchAdminTerm(term)"
            >
              {{ term.name }}
            </v-btn>
          </div>
        </div>
        <div class="pb-5">
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
            rows="3"
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
            Fetching sections...
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
import {partition, size, split, trim} from 'lodash'
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
    isInvalidUID() {
      return !!this.trim(this.uid) && !this.uid.match(/^\d+$/)
    }
  },
  data: () => ({
    sectionIds: '',
    error: undefined,
    uid: undefined
  }),
  methods: {
    setMode(mode) {
      this.setAdminMode(mode)
      if (mode === 'bySectionId') {
        this.$announcer.polite('Input mode switched to section ID')
        putFocusNextTick('load-sections-by-id')
      } else {
        this.$announcer.polite(`Input mode switched to ${mode === 'bySectionId' ? 'section ID' : 'UID'}`)
        putFocusNextTick(mode === 'bySectionId' ? 'load-sections-by-id' : 'instructor-uid')
      }
    },
    size,
    submit() {
      if (this.adminMode === 'bySectionId') {
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
      } else {
        const trimmed = trim(this.uid)
        if (/^\d+$/.test(trimmed)) {
          this.setAdminActingAs(trimmed)
          this.fetchFeed()
        } else {
          this.error = 'UID must be numeric.'
          putFocusNextTick('instructor-uid')
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
.page-create-course-site-act-as-form {
  margin: 5px 0;
  input[type="text"] {
    font-family: $body-font-family;
    font-size: 14px;
    margin: 2px 10px 0 0;
    padding: 8px 12px;
    width: 140px;
  }
}
.page-create-course-site-header {
  color: $color-headers;
  font-family: $body-font-family;
  font-weight: normal;
  line-height: 40px;
  margin: 5px 0;
}
.has-error {
  color: $color-alert-error-foreground;
  font-size: 14px;
  font-weight: bolder;
}
</style>
