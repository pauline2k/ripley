<template>
  <div class="px-4">
    <h2 class="sr-only">Administrator Options</h2>
    <div id="radio-group-modes" class="text-subtitle-1">Choose courses by:</div>
    <v-radio-group
      v-model="adminModeModel"
      aria-labelledby="radio-group-modes"
      color="primary"
      density="compact"
      :disabled="isFetching"
      hide-details
    >
      <v-radio
        id="radio-btn-mode-act-as"
        aria-label="Instructor"
        class="pt-1"
        value="actAs"
      >
        <template #label>
          <div aria-hidden="true" class="pl-1r text-black text-body-2">Instructor</div>
        </template>
      </v-radio>
      <v-radio
        id="radio-btn-mode-section-id"
        aria-label="Section I Deez"
        class="pt-1"
        value="bySectionId"
      >
        <template #label>
          <div aria-hidden="true" class="pl-1r text-black text-body-2">Section IDs</div>
        </template>
      </v-radio>
    </v-radio-group>
    <div v-if="adminMode === 'actAs'" class="pt-4">
      <div class="align-center d-flex flex-wrap pb-3">
        <v-text-field
          id="instructor-uid"
          v-model="uid"
          aria-label="Instructor U I D"
          autocomplete="on"
          class="instructor-uid-text-field mr-2r mt-3"
          density="comfortable"
          :disabled="isFetching"
          :error="isInvalidUID"
          hide-details
          label="Instructor UID"
          maxlength="16"
          variant="outlined"
          @keydown.enter="submit"
        />
        <v-btn
          id="sections-by-uid-button"
          aria-label="Load official sections for instructor"
          class="mt-3"
          color="primary"
          :disabled="isFetching || !trim(uid) || isInvalidUID"
          size="large"
          @click="submit"
        >
          <span v-if="isFetching">
            <SpinnerWithinButton />
            Fetching...
          </span>
          <span v-if="!isFetching">As instructor</span>
        </v-btn>
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
          <v-textarea
            id="page-create-course-site-section-id-list"
            v-model="sectionIds"
            aria-label="Paste your list of Section IDs here, separated by commas or spaces"
            auto-grow
            :disabled="isFetching"
            hide-details
            max-width="60rem"
            placeholder="Paste your list of Section IDs here, separated by commas or spaces"
            rows="2"
            variant="outlined"
          />
        </div>
        <v-btn
          id="sections-by-ids-button"
          color="primary"
          :disabled="!trim(sectionIds) || isFetching"
          @click="submit"
        >
          <span v-if="isFetching">
            <SpinnerWithinButton />
            Fetching...
          </span>
          <span v-if="!isFetching">Find Matching Sections</span>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, ref, watch} from 'vue'
import {find, partition, size, split, trim} from 'lodash'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {putFocusNextTick} from '@/utils'

const props = defineProps({
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
  setWarning: {
    required: true,
    type: Function
  },
  switchAdminTerm: {
    required: true,
    type: Function
  }
})

const sectionIds = ref('')
const uid = ref()

const adminModeModel = defineModel('adminModeModel', {
  get() {
    return props.adminMode
  },
  set(mode) {
    props.setWarning(null)
    sectionIds.value = ''
    uid.value = undefined
    props.setAdminMode(mode)
  },
  type: String
})

const isInvalidUID = computed(() => {
  return !!trim(uid.value) && !uid.value.match(/^\d+$/)
})

const slug = defineModel('slug', {
  get() {
    return props.currentAdminTerm
  },
  set(slug) {
    const term = find(props.adminTerms, ['slug', slug])
    props.switchAdminTerm(term)
  },
  type: String
})

watch(sectionIds, () => {
  props.setWarning(null)
})
watch(uid, () => {
  props.setWarning(null)
})

const submit = () => {
  if (!props.isFetching) {
    if (props.adminMode === 'bySectionId' && trim(sectionIds.value)) {
      const trimmed = trim(sectionIds.value)
      const sectionIdsList = split(trimmed, /[,\r\n\t ]+/)
      const notNumeric = partition(sectionIdsList, sectionId => /^\d+$/.test(trim(sectionId)))[1]
      if (notNumeric.length) {
        props.setWarning('Section IDs must be numeric.')
        putFocusNextTick('page-create-course-site-section-id-list')
      } else {
        props.setAdminBySectionIds(sectionIdsList)
        props.fetchFeed()
      }
    } else if (props.adminMode === 'actAs' && trim(uid.value) && !isInvalidUID.value) {
      const trimmed = trim(uid.value)
      if (/^\d+$/.test(trimmed)) {
        props.setAdminActingAs(trimmed)
        props.fetchFeed()
      } else {
        props.setWarning('UID must be numeric.')
        putFocusNextTick('instructor-uid')
      }
    }
  }
}
</script>

<style scoped lang="scss">
.instructor-uid-text-field {
  flex-grow: 0;
  min-width: 12rem;
}
.term-btn-toggle {
  border-width: 1px;
}
</style>
