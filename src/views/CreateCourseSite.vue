<template>
  <div class="pb-5 px-5">
    <Header1 class="mb-2 ml-3" text="Create a Course Site" />
    <div aria-live="assertive" role="alert">
      <v-alert
        v-if="error"
        id="create-site-error"
        class="my-3 ml-2"
        density="compact"
        role="none"
        :text="error"
        type="error"
      />
    </div>
    <div aria-live="polite">
      <v-alert
        v-if="warning"
        id="create-site-warning"
        class="my-3 ml-2"
        density="compact"
        role="none"
        :text="warning"
        type="warning"
      />
    </div>
    <div v-if="!contextStore.isLoading && !error">
      <div v-if="isAdmin && currentWorkflowStep !== 'processing'" class="pl-3">
        <CreateCourseSiteHeader
          :admin-mode="adminMode"
          :admin-terms="adminTerms"
          :current-admin-term="currentAdminTerm"
          :fetch-feed="fetchFeed"
          :is-fetching="isFetching"
          :set-admin-acting-as="setAdminActingAs"
          :set-admin-by-section-ids="setAdminBySectionIds"
          :set-admin-mode="setAdminMode"
          :set-warning="w => warning = w"
          :switch-admin-term="switchAdminTerm"
        />
      </div>
      <div v-if="!isFetching" :class="{'pt-2': isAdmin && currentWorkflowStep !== 'processing'}">
        <div v-if="currentWorkflowStep === 'selecting' && size(teachingTerms)">
          <v-card class="mt-2" elevation="0">
            <v-tabs
              v-if="size(teachingTerms) > 1"
              v-model="selectedTerm"
              aria-label="Official Sections"
              class="tabs-border"
              color="primary"
              slider-color="grey-darken-3"
            >
              <v-tab
                v-for="(term, index) in teachingTerms"
                :id="`term${index}`"
                :key="index"
                aria-controls="official-sections-tabpanel"
                :aria-selected="term.slug === selectedTerm"
                class="tab-term-select"
                :class="{'rounded-ts-lg': index === 0, 'rounded-te-lg': index === 1}"
                :tabindex="term.slug === selectedTerm ? 0 : -1"
                :value="term.slug"
                variant="elevated"
              >
                <span
                  class="font-size-16"
                  :class="{'text-white': term.slug === selectedTerm, 'text-primary': term.slug !== selectedTerm}"
                >
                  {{ term.name }}
                </span>
              </v-tab>
            </v-tabs>
            <div class="border pb-5 px-5 pt-3">
              <v-window
                id="official-sections-tabpanel"
                v-model="selectedTerm"
                :aria-labelledby="size(teachingTerms) > 1 ? `term${findIndex(teachingTerms, t => t.slug === selectedTerm)}` : undefined"
                :role="size(teachingTerms) > 1 ? 'tabpanel' : undefined"
              >
                <v-window-item :value="selectedTerm">
                  <h2 id="official-sections-heading">
                    {{ selectedTermName }}
                    {{ actingAsInstructor ? `sections taught by ${actingAsInstructor.name}` : 'Official Sections' }}
                  </h2>
                  <div v-if="size(coursesList)">
                    <div class="text-subtitle-1 mt-1 mb-3">
                      All official sections you select below will be put in ONE, single course site.
                    </div>
                    <SelectSectionsGuide />
                    <v-expansion-panels
                      v-model="panels"
                      class="my-5"
                      multiple
                    >
                      <v-expansion-panel
                        v-for="course in coursesList"
                        :id="`sections-course-${course.slug}`"
                        :key="course.course_id"
                        :value="course.slug"
                        bg-color="blue-lighten-5"
                      >
                        <v-expansion-panel-title :id="`sections-course-${course.slug}-btn`">
                          <template #actions="{ expanded }">
                            <v-icon :icon="expanded ? mdiMenuDown : mdiMenuRight" />
                          </template>
                          <h3 :id="`sections-course-title-${course.slug}`" class="sections-course-title">
                            <CourseCodeAndTitle :course="course" />
                          </h3>
                        </v-expansion-panel-title>
                        <v-expansion-panel-text>
                          <CourseSectionsTable
                            :id="`template-sections-table-${course.slug}`"
                            :key="course.slug"
                            class="mb-1 mt-4"
                            mode="createCourseForm"
                            :sections="course.sections"
                            :table-caption="courseSectionsTableCaption(course)"
                            table-clazz="border-0"
                            :update-selected="updateSelected"
                          />
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </div>
                  <div v-if="!size(coursesList)" class="text-subtitle-1 mt-1 mb-3">
                    No matching course sections found.
                  </div>
                </v-window-item>
              </v-window>
              <div class="d-flex justify-end mt-2">
                <v-btn
                  id="page-create-course-site-continue"
                  aria-label="Continue to next step"
                  class="mr-2"
                  color="primary"
                  :disabled="!selectedSectionsList.length"
                  @click="showConfirmation"
                >
                  Next
                </v-btn>
                <v-btn
                  id="page-create-course-site-cancel"
                  aria-label="Cancel and return to Site Creation Overview"
                  variant="tonal"
                  @click="cancel"
                >
                  Cancel
                </v-btn>
              </div>
            </div>
          </v-card>
        </div>
        <div v-if="currentWorkflowStep === 'confirmation'">
          <ConfirmationStep
            :course-site-creation-promise="courseSiteCreationPromise"
            :current-semester-name="currentSemesterName"
            :go-back="onCancelConfirmationStep"
            :selected-sections-list="selectedSectionsList"
          />
        </div>
        <div
          v-if="currentWorkflowStep === 'processing'"
          aria-live="polite"
        >
          <div class="pl-8 pr-16 py-4">
            <div class="pb-3">
              <span v-if="jobStatus === 'sendingRequest'">Sending request...</span>
              <span v-if="jobStatus === 'queued'">Request sent. Awaiting processing...</span>
              <span v-if="jobStatus === 'started'">Request received. Provisioning course site...</span>
              <span v-if="jobStatus === 'finished'">Finishing up...</span>
            </div>
            <v-progress-linear
              color="primary"
              height="10"
              indeterminate
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {each, find, findIndex, get, includes, map, size} from 'lodash'
import {mdiMenuDown, mdiMenuRight} from '@mdi/js'
import {useRouter} from 'vue-router'
import ConfirmationStep from '@/components/bcourses/create/ConfirmationStep'
import CourseCodeAndTitle from '@/components/bcourses/create/CourseCodeAndTitle'
import CourseSectionsTable from '@/components/bcourses/CourseSectionsTable'
import CreateCourseSiteHeader from '@/components/bcourses/create/CreateCourseSiteHeader'
import Header1 from '@/components/utils/Header1'
import SelectSectionsGuide from '@/components/bcourses/create/SelectSectionsGuide'
import {alertScreenReader, iframeParentLocation, isInIframe, putFocusNextTick} from '@/utils'
import {courseCreate, courseProvisionJobStatus, getCourseProvisioningMetadata, getSections} from '@/api/canvas-site'
import {useContextStore} from '@/stores/context'

const actingAsInstructor = ref(undefined)
const adminActingAs = ref(undefined)
const adminBySectionIds = ref(undefined)
const adminMode = ref('actAs')
const adminTerms = ref([])
const backgroundJobId = ref(undefined)
const contextStore = useContextStore()
const coursesList = ref([])
const currentAdminTerm = ref('')
const currentSemester = ref(undefined)
const currentSemesterName = ref(undefined)
const currentWorkflowStep = ref(undefined)
const error = ref(undefined)
const isFetching = ref(false)
const jobStatus = ref(undefined)
const panels = ref([])
const percentComplete = ref(undefined)
const router = useRouter()
const selectedSectionsList = ref(undefined)
const selectedTerm = ref(undefined)
const teachingTerms = ref([])
const warning = ref(undefined)

const isAdmin = computed(() => {
  return contextStore.currentUser.isAdmin || contextStore.currentUser.isCanvasAdmin
})
const selectedTermName = computed(() => {
  const term = find(teachingTerms.value, t => t.slug === selectedTerm.value)
  return get(term, 'name', '')
})

watch(selectedTerm, slug => {
  if (slug) {
    updateSemesterData(slug)
  }
})

onMounted(() => {
  getCourseProvisioningMetadata().then(data => {
    updateMetadata(data)
    if (!teachingTerms.value.length && !isAdmin.value) {
      warning.value = 'You are not listed as an instructor of any courses in the current or upcoming term.'
    }
    if (size(selectedSectionsList.value)) {
      panels.value = Array.from({length: coursesList.value.length}, (value, index) => index)
    } else if (coursesList.value.length === 1) {
      panels.value = [0]
    }
    actingAsInstructor.value = getActingAsInstructor()

    contextStore.loadingComplete()
  }, errorMessage => {
    error.value = errorMessage
    contextStore.loadingComplete()
  })
})

const cancel = () => {
  router.push({path: '/manage_sites'})
}

const classCount = semesters => {
  let count = 0
  if (size(semesters) > 0) {
    each(semesters, semester => {
      count += semester.classes.length
    })
  }
  return count
}

const courseSectionsTableCaption = course => {
  let caption = 'Official sections in this course. Use the checkboxes in the Action column to select sections'
  if (size(course.sections) > 1) {
    caption += ', or use the "Select All" button above.'
  }
  return caption
}

const courseSiteCreationPromise = (siteName, siteAbbreviation) => {
  return new Promise((resolve, reject) => {
    const onError = message => {
      percentComplete.value = 0
      currentWorkflowStep.value = null
      jobStatus.value = 'error'
      warning.value = message
      putFocusNextTick('page-title')
      reject()
    }
    currentWorkflowStep.value = 'processing'
    jobStatus.value = 'sendingRequest'
    updateSelected()
    const sectionIds = map(selectedSectionsList.value, 'id')
    if (sectionIds.length > 0) {
      const adminActingAsArg = isAdmin.value && adminMode.value === 'actAs' ? adminActingAs.value : null
      const adminBySectionIdsArg = isAdmin.value && adminMode.value === 'bySectionId' ? adminBySectionIds.value : null
      const adminTermSlugArg = isAdmin.value && adminMode.value === 'bySectionId' ? currentAdminTerm.value : null
      courseCreate(
        adminActingAsArg,
        adminBySectionIdsArg,
        adminTermSlugArg,
        sectionIds,
        siteAbbreviation,
        siteName,
        currentSemester.value
      ).then(
        data => {
          backgroundJobId.value = data.jobId
          jobStatus.value = data.jobStatus
          alertScreenReader('Started course site creation.')
          trackBackgroundJob()
          resolve()
        },
        () => onError('Failed to start course provisioning job.')
      )
    } else {
      onError('No section IDs were provided.')
    }
  })
}

const fetchFeed = () => {
  warning.value = null
  isFetching.value = true
  currentWorkflowStep.value = 'selecting'
  backgroundJobId.value = undefined
  jobStatus.value = undefined
  percentComplete.value = undefined
  selectedSectionsList.value = []
  alertScreenReader('Loading courses and sections')

  const semester = (adminMode.value === 'bySectionId' ? currentAdminTerm.value : currentSemester.value)
  getSections(
    adminActingAs.value,
    adminBySectionIds.value,
    adminMode.value,
    semester,
    isAdmin.value
  ).then(
    data => {
      updateMetadata(data)
      const usersClassCount = classCount(data.teachingTerms)
      teachingTerms.value = data.teachingTerms
      if (!teachingTerms.value.length && adminMode.value) {
        warning.value = adminActingAs.value ? `UID ${adminActingAs.value} is not listed as an instructor of any courses in the current or upcoming term.` : 'No matching courses found.'
      }
      fillCourseSites(teachingTerms.value)
      alertScreenReader('Course sections have loaded')
      if (adminMode.value === 'bySectionId' && adminBySectionIds.value) {
        each(coursesList.value, course => {
          each(course.sections, section => {
            section.selected = includes(adminBySectionIds.value, section.id)
          })
        })
        updateSelected()
      }
      if (!isAdmin.value && !usersClassCount) {
        warning.value = 'Sorry, you are not an admin user and you have no classes.'
      }
    },
    error => {
      alertScreenReader('Course section loading failed')
      warning.value = error || 'failure'
    }
  ).finally(() => {
    isFetching.value = false
    putFocusNextTick(adminMode.value === 'bySectionId' ? 'sections-by-ids-button' : 'sections-by-uid-button')
  })
}

const fillCourseSites = semestersFeed => {
  each(semestersFeed, semester => {
    each(semester.classes, course => {
      course.allSelected = false
      course.selectToggleText = 'All'
      const hasSites = false
      const sectionIdToSites = {}
      if (hasSites) {
        course.hasSites = hasSites
        each(course.sections, section => {
          if (sectionIdToSites[section.id]) {
            section.sites = sectionIdToSites[section.id]
          }
        })
      }
    })
  })
}

const getActingAsInstructor = () => {
  let instructor
  if (adminActingAs.value) {
    each(teachingTerms.value, t => each(t.classes, c => each(c.sections, s => each(s.instructors, i => {
      if (i.uid === adminActingAs.value) {
        instructor = i
        return false
      }
    }))))
  }
  return instructor
}

const onCancelConfirmationStep = () => {
  currentWorkflowStep.value = 'selecting'
}

const setAdminActingAs = uid => {
  adminActingAs.value = uid
  adminBySectionIds.value = null
}

const setAdminBySectionIds = sectionIds => {
  adminBySectionIds.value = sectionIds
  adminActingAs.value = null
}

const setAdminMode = mode => {
  adminMode.value = mode
  currentWorkflowStep.value = undefined
  coursesList.value = []
}

const setTermSlug = slug => {
  if (selectedTerm.value === slug) {
    updateSemesterData(selectedTerm.value)
  } else {
    // If the selectedTerm value is changing, updateSemesterData will be called by the 'watch' property set above
    selectedTerm.value = slug
  }
}

const showConfirmation = () => {
  updateSelected()
  alertScreenReader('Course site details form loaded.')
  currentWorkflowStep.value = 'confirmation'
}

const switchAdminTerm = semester => {
  if (semester && currentAdminTerm.value !== semester.slug) {
    currentWorkflowStep.value = null
    currentAdminTerm.value = semester.slug
    selectedSectionsList.value = []
    updateSelected()
  }
}

const trackBackgroundJob = () => {
  const exportTimer = setInterval(() => {
    courseProvisionJobStatus(backgroundJobId.value).then(
      response => {
        if (response.jobStatus !== jobStatus.value) {
          jobStatus.value = response.jobStatus
        } else {
          alertScreenReader(`Still ${includes(['sendingRequest', 'queued'], jobStatus.value) ? 'waiting' : 'processing'}`)
        }
        if (!(includes(['started', 'queued'], jobStatus.value)) || get(response, 'jobData.courseSiteUrl')) {
          clearInterval(exportTimer)
          if (get(response, 'jobData.courseSiteUrl')) {
            alertScreenReader('Done. Loading new course site.')
            if (isInIframe) {
              iframeParentLocation(response.jobData.courseSiteUrl)
            } else {
              window.location.href = response.jobData.courseSiteUrl
            }
          } else {
            alertScreenReader('Error.', 'assertive')
            currentWorkflowStep.value = null
            jobStatus.value = 'error'
            warning.value = 'An error has occurred with your request. Please try again or contact bCourses support.'
            putFocusNextTick('page-title')
          }
        }
      }
    ).catch(
      () => {
        alertScreenReader('Error.', 'assertive')
        currentWorkflowStep.value = null
        jobStatus.value = 'error'
        warning.value = 'An error has occurred with your request. Please try again or contact bCourses support.'
        clearInterval(exportTimer)
        putFocusNextTick('page-title')
      }
    )
  }, 4000)
}

const updateMetadata = data => {
  teachingTerms.value = data.teachingTerms
  if (size(teachingTerms.value) > 0) {
    setTermSlug(teachingTerms.value[0].slug)
  }
  fillCourseSites(teachingTerms.value)
  if (isAdmin.value) {
    adminActingAs.value = data.adminActingAs
    adminTerms.value = data.adminTerms
    if (size(teachingTerms.value) > 0 && adminTerms.value.length) {
      setTermSlug(teachingTerms.value[0].slug)
    }
    if (size(adminTerms.value) > 0 && !currentAdminTerm.value) {
      switchAdminTerm(adminTerms.value[0])
    }
  } else {
    currentWorkflowStep.value = 'selecting'
  }
}

const updateSelected = () => {
  selectedSectionsList.value = []
  each(coursesList.value, course => {
    each(course.sections, section => {
      if (section.selected) {
        section.courseTitle = course.title
        selectedSectionsList.value.push(section)
      }
    })
  })
}

const updateSemesterData = slug => {
  const teachingTerm = find(teachingTerms.value, t => t.slug === slug)
  const term = teachingTerm || find(adminTerms.value, t => t.slug === slug)
  coursesList.value = teachingTerm ? teachingTerm.classes : []
  currentSemester.value = slug
  currentSemesterName.value = term.name
  selectedSectionsList.value = []
  alertScreenReader(`Course sections for ${term.name} loaded`)
  updateSelected()
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type -->
<style>
.v-expansion-panel-text__wrapper {
  padding: 8px 12px 16px !important;
}
</style>

<style scoped lang="scss">
.sections-course-title {
  font-size: 0.938rem !important;
  font-weight: 700 !important;
  line-height: 15px;
}
.tab-term-select {
  flex-grow: 1;
}
.tabs-border {
  -moz-border-radius: 0;
  -webkit-border-radius: 8px 8px 0 0;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px 8px 0 0;
}
</style>
