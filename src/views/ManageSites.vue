<template>
  <div v-if="!contextStore.isLoading" class="pt-3 px-4 px-sm-8 px-lg-16">
    <Header1 class="mb-2" text="Create or Update bCourses Sites" />
    <div aria-live="assertive" role="alert">
      <v-alert
        v-if="error"
        id="error-alert"
        class="my-2"
        density="compact"
        role="none"
        :text="error"
        type="error"
      />
    </div>
    <v-radio-group
      v-model="selection"
      :aria-activedescendant="get(selection, 'id')"
      aria-label="site management options"
      hide-details
    >
      <div
        v-for="option in options"
        :key="option.id"
        class="option d-flex mb-1 pb-2"
        :class="{
          'highlight-when-hover': selection !== option,
          'highlight-when-selected': selection === option
        }"
      >
        <div class="radio-button-container">
          <v-radio
            :id="option.id"
            :aria-checked="selection === option"
            :class="{'text-disabled': !option.isAvailable}"
            :disabled="!option.isAvailable || isProcessing"
            :value="option"
          />
        </div>
        <div class="list-item-content on-surface">
          <label
            class="font-size-20"
            :class="{
              'text-medium-emphasis': !option.isAvailable,
              'on-surface': option.isAvailable
            }"
            :for="option.id"
          >
            {{ option.header }}
          </label>
          <div v-if="option.id === 'create-course-site'">
            <div v-if="option.isAvailable" @click="() => selection = option">
              Set up course sites to communicate with and manage the work of students enrolled in your classes.
            </div>
            <div v-if="!option.isAvailable" class="text-medium-emphasis">
              To create a course site, you will need to be the official instructor of record for a course.
              If you have not been assigned as the official instructor of record for the course,
              please contact your department scheduler.
              You will be able to create a course site the day after you have been officially assigned to teach the course.
            </div>
          </div>
          <div
            v-if="option.id === 'create-project-site'"
            class="on-surface"
            :class="{'text-medium-emphasis': !option.isAvailable}"
            @click="() => selection = option"
          >
            Share files and collaborate. Project sites are best suited for instructors and <span :aria-hidden="true">GSIs</span><span class="sr-only">G S I's</span> who already use bCourses.
            Project sites cannot access all bCourses features and are not intended for lecture, lab, or discussion sections.
            <OutboundLink id="bcourses-project-sites-service-page" href="https://rtl.berkeley.edu/services-programs/bcourses-project-sites">Learn more about Project Sites</OutboundLink>
            and
            <OutboundLink
              id="berkeley-collaboration-services-information"
              href="https://bconnected.berkeley.edu/collaboration-services"
              period-terminated
              text="other collaboration tools at UC Berkeley"
            />
          </div>
          <div v-if="option.id === 'manage-official-sections'" class="pt-2" @click="() => selection = option">
            <div v-if="!size(coursesByTerm) && !isAdmin" class="text-medium-emphasis">
              Please create a {{ config.terms.current.name }} or {{ config.terms.next.name }}
              course site in order to use the Manage Official Sections tool.
            </div>
            <div v-if="size(coursesByTerm)" :class="{'text-medium-emphasis': !option.isAvailable}">
              <div>
                Add or remove official section rosters in already-created course sites.
              </div>
              <div v-if="option.isAvailable" class="py-2">
                <select
                  id="course-sections"
                  v-model="canvasSiteId"
                  aria-label="All your courses"
                  autocomplete="off"
                  :disabled="isManageOfficialSectionsDisabled"
                >
                  <option :value="undefined">Choose a course</option>
                  <optgroup
                    v-for="(courses, termId) in coursesByTerm"
                    :key="termId"
                    class="text-subtitle-1"
                    :label="getTermName(termId)"
                  >
                    <option
                      v-for="course in labelCourses(courses)"
                      :id="`canvas-site-${course.canvasSiteId}`"
                      :key="course.canvasSiteId"
                      :aria-label="`${getTermName(termId)} group: ${course.courseCode} ${course.name}`"
                      :value="course.canvasSiteId"
                      v-html="course.label"
                    />
                  </optgroup>
                </select>
              </div>
            </div>
            <div v-if="isAdmin" class="mt-2">
              <v-text-field
                id="canvas-site-id-input"
                v-model="canvasSiteId"
                autocomplete="on"
                density="compact"
                :disabled="isManageOfficialSectionsDisabled"
                :error="!!error || (!!trim(canvasSiteId) && !isCanvasSiteIdValid)"
                hide-details
                label="Canvas Site ID"
                maxlength="9"
                max-width="10rem"
                variant="outlined"
                @keydown.enter="goNext"
              />
            </div>
            <div
              v-if="error"
              class="font-weight-medium text-red"
            >
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </v-radio-group>
    <v-btn
      id="go-next-btn"
      class="d-flex ml-auto mt-3"
      color="primary"
      :disabled="isButtonDisabled || isProcessing"
      size="large"
      @click="goNext"
    >
      <span v-if="isProcessing">
        <SpinnerWithinButton /> Next
      </span>
      <span v-if="!isProcessing">Next</span>
    </v-btn>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {each, get, map, size, trim, uniq} from 'lodash'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink.vue'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import type {CanvasSite} from '@/lib/types'
import {getCanvasSite, getManageOfficialSections} from '@/api/canvas-site'
import {getSiteCreationAuthorizations} from '@/api/canvas-utility'
import {getTermName, isValidCanvasSiteId, putFocusNextTick} from '@/utils'
import {useContextStore} from '@/stores/context'
import {useRouter} from 'vue-router'

const contextStore = useContextStore()
const canvasSiteId = ref()
const coursesByTerm = ref<Record<string, CanvasSite[]>>({})
const config = contextStore.config
const currentUser = contextStore.currentUser
const error = ref()
const isProcessing = ref<boolean>()
const options = ref()
const router = useRouter()
const selection = ref()

const isAdmin = computed(() => {
  return currentUser.isAdmin || currentUser.isCanvasAdmin
})
const isButtonDisabled = computed(() => {
  return !selection.value || (selection.value.id === 'manage-official-sections' && !isCanvasSiteIdValid.value)
})
const isCanvasSiteIdValid = computed(() => {
  return isValidCanvasSiteId(canvasSiteId.value)
})
const isManageOfficialSectionsDisabled = computed(() => {
  return !selection.value || selection.value.id !== 'manage-official-sections' || isProcessing.value
})

watch(selection, () => {
  canvasSiteId.value = undefined
})

onMounted(() => {
  coursesByTerm.value = {}
  getManageOfficialSections(false).then((data: Record<string, CanvasSite[]>) => {
    each(data, (courses: CanvasSite[], term) => {
      if (courses.length) {
        coursesByTerm.value[term] = courses
      }
    })
    getSiteCreationAuthorizations().then(data => {
      const canCreateCourseSite = data.authorizations.canCreateCourseSite
      const canCreateProjectSite = data.authorizations.canCreateProjectSite
      options.value = [
        {
          header: 'Create a course site',
          id: 'create-course-site',
          isAvailable: canCreateCourseSite,
          label: 'Create a Course Site',
          path: '/create_course_site'
        },
        {
          header: 'Create a project site',
          id: 'create-project-site',
          isAvailable: canCreateProjectSite,
          label: 'Create a Project Site',
          path: '/create_project_site'
        },
        {
          header: 'Manage official sections of an existing site',
          id: 'manage-official-sections',
          isAvailable: isAdmin.value || size(coursesByTerm.value),
          label: 'Manage Official Sections',
          path: '/manage_sites'
        }
      ]
      if (!canCreateCourseSite && !canCreateProjectSite) {
        selection.value = options.value[2]
      }
      contextStore.loadingComplete()
    })
  }, data => {
    error.value = data
    contextStore.loadingComplete()
  })
})

const goNext = () => {
  if (!isButtonDisabled.value) {
    isProcessing.value = true
    if (selection.value.id === 'manage-official-sections') {
      getCanvasSite(canvasSiteId.value).then(
        () => router.push({path: `/official_sections/${canvasSiteId.value}`}),
        data => {
          error.value = data
          putFocusNextTick('canvas-site-id-input')
        }
      ).finally(() => isProcessing.value = false)
    } else {
      router.push({path: selection.value.path})
      isProcessing.value = false
    }
  }
}

const labelCourses = (courses: CanvasSite[]) => {
  const getLabel = (course: CanvasSite, enhance?: boolean) => {
    const prefix = enhance ? `${course.canvasSiteId}: ` : ''
    return `${prefix}${course.courseCode} &mdash; ${course.name}`
  }
  const enhance = uniq(map(courses, c => getLabel(c))).length !== courses.length
  return map(courses, c => ({...c, label: getLabel(c, enhance)}))
}
</script>

<style scoped lang="scss">
.highlight-when-hover:hover {
  background-color: rgba(var(--v-theme-surface-light));
}
.highlight-when-selected {
  background-color: rgba(var(--v-theme-surface-variant));
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity)) !important;
}
.option {
  border: 1px solid transparent;
  padding-inline: 1rem;
}
.list-item-content {
  padding: 0.3rem 8px 12px 0;
}
.radio-button-container {
  padding: 0 0.75rem 0 0;
}
</style>
