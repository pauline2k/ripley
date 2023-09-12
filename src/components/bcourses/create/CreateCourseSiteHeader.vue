<template>
  <div class="page-create-course-site-admin-options">
    <h2 class="sr-only">Administrator Options</h2>
    <v-btn
      id="toggle-admin-mode-button"
      aria-controls="page-create-course-site-admin-section-loader-form"
      class="page-create-course-site-admin-mode-switch pb-2 ptl-3 pr-2 pt-2"
      color="primary"
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
                  aria-controls="page-create-course-site-steps-container"
                  aria-label="Load official sections for instructor"
                  color="primary"
                  type="submit"
                  :disabled="!uid"
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
          <div v-if="size(adminTerms)">
            <span v-for="(term, index) in adminTerms" :key="index">
              <v-btn
                :id="`term${index}`"
                name="adminTerm"
                :aria-selected="currentAdminTerm === term.slug"
                :color="currentAdminTerm === term.slug ? 'primary' : ''"
                role="tab"
                @click="switchAdminTerm(term)"
                @keyup.enter="switchAdminTerm(term)"
              >
                {{ term.name }}
              </v-btn>
            </span>
            <label
              for="page-create-course-site-section-id-list"
              class="sr-only"
            >
              Provide Section ID List Separated by Commas or Spaces
            </label>
            <div>
              <textarea
                id="page-create-course-site-section-id-list"
                v-model="sectionIds"
                class="page-create-course-site-section-id-input"
                placeholder="Paste your list of Section IDs here, separated by commas or spaces"
              ></textarea>
            </div>
            <v-btn
              id="sections-by-ids-button"
              aria-controls="page-create-course-site-steps-container"
              color="primary"
              type="submit"
              :disabled="!trim(sectionIds)"
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
import {partition, size, trim} from 'lodash'
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
    size,
    submit() {
      if (this.adminMode === 'bySectionId') {
        const trimmed = trim(this.sectionIds)
        const split = split(trimmed, /[,\r\n\t ]+/)
        const notNumeric = partition(split, sectionId => /^\d+$/.test(trim(sectionId)))[1]
        if (notNumeric.length) {
          this.error = 'Section IDs must be numeric.'
          putFocusNextTick('page-create-course-site-section-id-list')
        } else {
          this.setAdminBySectionIds(split)
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
.page-create-course-site-section-id-input {
  border: solid 1px;
  border-radius: 3px;
  font-family: Lato,Helvetica Neue,Helvetica,Arial,sans-serif;
  font-size: 14px;
  font-weight: 300;
  padding: 5px;
  width: 100%;
}
.has-error {
  color: $color-alert-error-foreground;
  font-size: 14px;
  font-weight: bolder;
}
</style>
