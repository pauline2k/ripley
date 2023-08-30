<template>
  <div class="page-create-course-site-admin-options">
    <h2 class="sr-only">Administrator Options</h2>
    <v-btn
      id="toggle-admin-mode-button"
      aria-controls="page-create-course-site-admin-section-loader-form"
      class="canvas-button canvas-button-small page-create-course-site-admin-mode-switch pb-2 ptl-3 pr-2 pt-2"
      @click="setMode(adminMode === 'actAs' ? 'bySectionId' : 'actAs')"
    >
      Switch to {{ adminMode === 'actAs' ? 'Section ID input' : 'acting as instructor' }}
    </v-btn>
    <div id="page-create-course-site-admin-section-loader-form">
      <div v-if="adminMode === 'actAs'">
        <h3 class="sr-only">Load Sections By Instructor UID</h3>
        <form
          id="page-create-course-site-act-as-form"
          class="canvas-page-form page-create-course-site-act-as-form"
          @submit.prevent="submit"
        >
          <v-row>
            <v-col cols="2">
              <label for="instructor-uid" class="sr-only">Instructor UID</label>
              <v-text-field
                id="instructor-uid"
                v-model="uid"
                density="compact"
                placeholder="Instructor UID"
                role="search"
                variant="outlined"
              ></v-text-field>
            </v-col>
            <v-col>
              <div>
                <v-btn
                  id="sections-by-uid-button"
                  type="submit"
                  class="canvas-button canvas-button-primary"
                  :disabled="!uid"
                  aria-label="Load official sections for instructor"
                  aria-controls="page-create-course-site-steps-container"
                >
                  As instructor
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </form>
      </div>
      <div v-if="adminMode === 'bySectionId'">
        <h3 id="load-sections-by-id" class="sr-only">Load Sections by ID</h3>
        <form id="load-sections-by-id-form" class="canvas-page-form" @submit.prevent="submit">
          <div v-if="$_.size(adminTerms)">
            <div class="buttonset">
              <span v-for="(term, index) in adminTerms" :key="index">
                <input
                  :id="`term${index}`"
                  type="radio"
                  name="adminTerm"
                  class="sr-only"
                  :aria-selected="currentAdminTerm === term.slug"
                  role="tab"
                  @click="switchAdminTerm(term)"
                  @keyup.enter="switchAdminTerm(term)"
                />
                <label
                  :for="`semester${index}`"
                  class="buttonset-button"
                  role="button"
                  aria-disabled="false"
                  :class="{
                    'buttonset-button-active': currentAdminTerm === semester.slug,
                    'buttonset-corner-left': index === 0,
                    'buttonset-corner-right': index === ($_.size(adminTerm) - 1)
                  }"
                >
                  {{ term.name }}
                </label>
              </span>
            </div>
            <label
              for="page-create-course-site-section-id-list"
              class="sr-only"
            >
              Provide Section ID List Separated by Commas or Spaces
            </label>
            <textarea
              id="page-create-course-site-section-id-list"
              v-model="sectionIds"
              placeholder="Paste your list of Section IDs here, separated by commas or spaces"
            />
            <v-btn
              id="sections-by-ids-button"
              class="canvas-button canvas-button-primary"
              aria-controls="page-create-course-site-steps-container"
              :disabled="!$_.trim(sectionIds)"
              type="submit"
            >
              Review matching Section IDs
            </v-btn>
          </div>
        </form>
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
  </div>
</template>

<script>
import Context from '@/mixins/Context'
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
    submit() {
      if (this.adminMode === 'bySectionId') {
        const trimmed = this.$_.trim(this.sectionIds)
        const split = this.$_.split(trimmed, /[,\r\n\t ]+/)
        const notNumeric = this.$_.partition(split, sectionId => /^\d+$/.test(this.$_.trim(sectionId)))[1]
        if (notNumeric.length) {
          this.error = 'Section IDs must be numeric.'
          putFocusNextTick('page-create-course-site-section-id-list')
        } else {
          this.setAdminBySectionIds(split)
          this.fetchFeed()
        }
      } else {
        const trimmed = this.$_.trim(this.uid)
        if (/^\d+$/.test(trimmed)) {
          this.setAdminActingAs(trimmed)
          this.fetchFeed()
        } else {
          this.error = 'UID must be numeric.'
          putFocusNextTick('instructor-uid')
        }
      }
    }
  }
}
</script>

<style scoped lang="scss">
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
.page-create-course-site-admin-options {
  margin-bottom: 15px;
}
.page-create-course-site-admin-mode-switch {
  margin-bottom: 5px;
  outline: none;
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
