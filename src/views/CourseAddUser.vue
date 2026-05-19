<template>
  <div v-if="!contextStore.isLoading" class="pb-5 px-8">
    <Header1 text="Find a Person to Add" />
    <NeedHelpFindingSomeone v-if="showSearchForm" class="py-1r" />
    <div
      id="alerts-container"
      class="px-3"
      aria-live="polite"
    >
      <div v-if="messages.errorStatus" class="alert alert-error align-center d-flex font-weight-medium">
        <div class="pr-2">
          <v-icon class="canvas-notice-icon" :icon="mdiAlert" />
        </div>
        <div>
          {{ messages.errorStatus }}
        </div>
        <div class="d-flex pl-4 ml-auto">
          <v-btn
            id="hide-search-error-button"
            aria-label="hide-alert"
            class="align-self-center bg-transparent text-error"
            density="compact"
            :icon="mdiCloseCircle"
            variant="flat"
            @click="hideAlert('errorStatus')"
          />
        </div>
      </div>
      <div v-if="messages.noUserSelectedAlert" class="alert alert-error align-center font-weight-medium d-flex">
        Please select a person from the search results.
        <div class="d-flex pl-4 ml-auto">
          <v-btn
            id="hide-select-user-alert-button"
            aria-label="hide-alert"
            class="align-self-center bg-transparent text-error"
            density="compact"
            :icon="mdiCloseCircle"
            variant="flat"
            @click="hideAlert('noUserSelectedAlert')"
          />
        </div>
      </div>
      <div v-if="messages.searchAlert" class="alert alert-error align-center font-weight-medium d-flex">
        {{ messages.searchAlert }}
        {{ searchTypeNotice }}
        Please try again.
        <div class="d-flex pl-4 ml-auto">
          <v-btn
            id="hide-search-alert-button"
            aria-label="hide-alert"
            class="align-self-center bg-transparent text-error"
            density="compact"
            :icon="mdiCloseCircle"
            variant="flat"
            @click="hideAlert('searchAlert')"
          >
            <v-icon :icon="mdiCloseCircle" />
            <span class="sr-only">Hide Alert</span>
          </v-btn>
        </div>
      </div>
      <div v-if="userSearchResultsCount > userSearchResults.length" class="alert alert-info font-weight-medium">
        Your search returned {{ userSearchResultsCount }} results, but only the first
        {{ userSearchResults.length }} are shown.
        Please refine your search to limit the number of results.
      </div>
      <div v-if="userSearchResultsCount && (userSearchResultsCount === userSearchResults.length)" class="sr-only">
        {{ pluralize('search result', userSearchResultsCount) }} loaded.
      </div>
      <div
        v-if="messages.additionSuccessMessage"
        id="success-message"
        class="alert alert-success align-center font-weight-medium d-flex"
        tabindex="-1"
      >
        <div>
          <span v-if="userAdded.sectionName">
            {{ userAdded.fullName }} was added to the &ldquo;{{ userAdded.sectionName }}&rdquo; section of this course
            as a <span aria-hidden="true">{{ userAdded.role }}.</span>
            <span class="sr-only">{{ srFriendlyRole(userAdded.role) }}.</span>
          </span>
          <span v-if="!userAdded.sectionName">
            {{ userAdded.fullName }} was added to the Canvas site as a <span aria-hidden="true">{{ userAdded.role }}.</span>
            <span class="sr-only">{{ srFriendlyRole(userAdded.role) }}.</span>
          </span>
        </div>
        <div class="d-flex pl-4 ml-auto">
          <v-btn
            id="hide-search-success-button"
            aria-label="hide alert"
            class="align-self-center bg-transparent text-success"
            density="compact"
            :icon="mdiCloseCircle"
            variant="flat"
            @click="hideAlert('additionSuccessMessage')"
          />
        </div>
      </div>
    </div>
    <v-container fluid>
      <v-row v-if="showSearchForm" no-gutters>
        <v-col>
          <v-row justify="center" no-gutters>
            <v-col cols="12">
              <div id="search-type-label" class="text-subtitle-1">Search By</div>
              <v-radio-group
                id="search-type"
                v-model="searchType"
                aria-controls="search-text"
                aria-labelledby="search-type-label"
                color="primary"
                density="compact"
                :disabled="isSearching || isAddingUser"
                hide-details
              >
                <v-radio
                  id="radio-btn-name"
                  aria-label="Last Name comma First Name"
                  class="mb-1r"
                  name="name"
                  value="name"
                >
                  <template #label>
                    <div aria-hidden="true" class="pl-1 text-black text-body-2">Last Name, First Name</div>
                  </template>
                </v-radio>
                <v-radio
                  id="radio-btn-email"
                  aria-label="Email"
                  class="mb-1r"
                  name="email"
                  value="email"
                >
                  <template #label>
                    <div aria-hidden="true" class="pl-1 text-black text-body-2">Email</div>
                  </template>
                </v-radio>
                <v-radio
                  id="radio-btn-uid"
                  aria-label="CalNet U I D"
                  class="mb-1r"
                  name="uid"
                  value="uid"
                >
                  <template #label>
                    <div aria-hidden="true" class="pl-1 text-black text-body-2">CalNet UID</div>
                  </template>
                </v-radio>
              </v-radio-group>
              <div class="align-center d-flex flex-wrap justify-space-between pb-4 w-100 w-lg-75">
                <div class="search-text-field">
                  <v-text-field
                    id="search-text"
                    v-model="searchText"
                    aria-autocomplete="none"
                    aria-describedby="alerts-container"
                    :aria-invalid="!!messages.searchAlert"
                    :aria-label="searchFieldAriaLabel"
                    :aria-labelledby="undefined"
                    autocomplete="off"
                    class="mt-4"
                    density="comfortable"
                    :disabled="isSearching || isAddingUser"
                    :error="!!messages.searchAlert"
                    hide-details
                    :label="searchFieldLabel"
                    variant="outlined"
                    @keydown.enter="submitSearch"
                  />
                </div>
                <div class="add-user-submit-search-btn-container w-100 w-sm-auto">
                  <v-btn
                    id="add-user-submit-search-btn"
                    aria-label="Submit search"
                    block
                    class="vertical-middle mt-4"
                    color="primary"
                    :disabled="!searchText || isSearching || isAddingUser"
                    size="large"
                    @click="submitSearch"
                  >
                    <span v-if="!isSearching">Search</span>
                    <span v-if="isSearching">
                      <SpinnerWithinButton /> Searching...
                    </span>
                  </v-btn>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row v-if="showUsersArea" no-gutters>
        <v-col v-if="userSearchResults.length > 0" md="12">
          <table id="person-search-results" class="table table-striped">
            <caption
              id="person-search-results-caption"
              class="text-left font-weight-bold pl-3 py-2"
              tabindex="-1"
            >
              {{ searchResultsHeadingText }}
              <span class="sr-only">Select the person you wish to add to the course site using the radio button in column one.</span>
            </caption>
            <thead>
              <tr>
                <th aria-sort="ascending" scope="col">Name</th>
                <th scope="col">
                  <span aria-hidden="true">Calnet UID</span>
                  <span class="sr-only">Calnet U I D</span>
                </th>
                <th scope="col">Email</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(user, index) in userSearchResults"
                :id="`user-search-result-row-${index}`"
                :key="user.uid"
                :class="{'bg-surface-variant border-md': selectedUser === user}"
              >
                <td :id="`user-search-result-row-select-${index}`" class="px-3 py-4 vertical-middle">
                  <v-radio
                    :id="`user-search-result-input-${index}`"
                    :model-value="selectedUser === user"
                    class="select-user-radio mr-4"
                    density="compact"
                    :disabled="isAddingUser"
                    :multiple="false"
                    @change="() => selectedUser = user"
                  >
                    <template #label>
                      {{ user.firstName }} {{ user.lastName }}
                    </template>
                  </v-radio>
                </td>
                <td
                  :id="`user-search-result-row-ldap-uid-${index}`"
                  class="px-3 py-4 vertical-middle"
                  data-label="CalNet UID"
                >
                  <span class="sr-only">{{ uidForScreenReader(user.uid) }}</span>
                  <span aria-hidden="true">{{ user.uid }}</span>
                </td>
                <td
                  :id="`user-search-result-row-email-${index}`"
                  class="px-3 py-4 vertical-middle"
                  data-label="Email"
                >
                  {{ user.emailAddress }}
                </td>
              </tr>
            </tbody>
          </table>
          <v-row class="mt-4">
            <v-col class="align-content-center pb-0 pb-sm-3" cols="12" sm="4">
              <label
                aria-hidden="true"
                class="align-center float-sm-right text-subtitle-1"
                for="user-role"
              >
                Role
              </label>
            </v-col>
            <v-col class="align-content-center pt-0 pt-sm-3" cols="12" sm="8">
              <select
                id="user-role"
                v-model="selectedRole"
                aria-label="Role"
                autocomplete="off"
                :disabled="isAddingUser"
              >
                <option
                  v-for="role in grantingRoles"
                  :key="role"
                  :aria-label="srFriendlyRole(role)"
                  :value="role"
                >
                  {{ role }}
                </option>
              </select>
            </v-col>
          </v-row>
          <v-row v-if="sections.length">
            <v-col class="align-content-center pb-0 pb-sm-3" cols="12" sm="4">
              <label
                aria-hidden="true"
                class="align-center float-sm-right text-subtitle-1"
                for="course-section"
              >
                Section
              </label>
            </v-col>
            <v-col class="align-content-center pt-0 pt-sm-3" cols="12" sm="8">
              <select
                id="course-section"
                v-model="sectionSelected"
                aria-label="Section"
                autocomplete="off"
                :disabled="isAddingUser"
              >
                <option v-for="section in sections" :key="section.name" :value="section">
                  {{ section.name }}
                </option>
              </select>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col cols="12">
              <div class="d-flex flex-wrap justify-end w-100">
                <v-btn
                  id="add-user-btn"
                  class="mt-4 ml-3 w-100 w-sm-auto"
                  color="primary"
                  :disabled="!selectedUser || isAddingUser"
                  @click="submitUser"
                >
                  <span v-if="!isAddingUser">Add Person</span>
                  <span v-if="isAddingUser">
                    <SpinnerWithinButton />Adding Person...
                  </span>
                </v-btn>
                <v-btn
                  id="start-over-btn"
                  class="mt-4 ml-3 w-100 w-sm-auto"
                  :disabled="isAddingUser"
                  @click="startOver"
                >
                  Reset
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import {computed, onMounted, reactive, ref} from 'vue'
import {find, get, replace, trim} from 'lodash'
import {mdiAlert, mdiCloseCircle} from '@mdi/js'
import Header1 from '@/components/utils/Header1'
import NeedHelpFindingSomeone from '@/components/utils/NeedHelpFindingSomeone'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton'
import {alertScreenReader, iframeScrollToTop, pluralize, putFocusNextTick} from '@/utils'
import {addUser, getAddUserOptions} from '@/api/canvas-user'
import {searchUsers} from '@/api/user'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const grantingRoles = ref([])
const isAddingUser = ref(false)
const isSearching = ref(false)
const messages = reactive({
  additionSuccessMessage: undefined,
  errorStatus: undefined,
  noUserSelectedAlert: false,
  searchAlert: undefined
})
const searchText = ref(undefined)
const searchType = ref('name')
const searchTypeNotice = ref(undefined)
const sections = ref([])
const sectionSelected = ref(undefined)
const selectedRole = ref(undefined)
const selectedUser = ref(undefined)
const showSearchForm = ref(undefined)
const showUsersArea = ref(undefined)
const userAdded = ref({})
const userSearchResultsCount = ref(0)
const userSearchResults = ref([])

const searchFieldAriaLabel = computed(() => {
  switch (searchType.value) {
  case 'name':
    return 'Search by last name comma first name'
  case 'email':
    return 'Search by email address'
  case 'uid':
    return 'Search by CalNet U I D'
  default:
    return 'Person search'
  }
})

const searchFieldLabel = computed(() => {
  switch (searchType.value) {
  case 'name':
    return 'e.g. Doe, Jane'
  case 'email':
    return 'name@berkeley.edu'
  case 'uid':
    return 'e.g. 123456789'
  default:
    return ''
  }
})

const searchResultsCountForDisplay = computed(() => {
  return userSearchResultsCount.value || userSearchResults.value.length
})

const searchResultsHeadingText = computed(() => {
  return `Search results: ${pluralize('user', searchResultsCountForDisplay.value)} found`
})

const selectedUserFullName = computed(() => {
  return `${selectedUser.value.firstName} ${selectedUser.value.lastName}`
})

onMounted(() => {
  getAddUserOptions(contextStore.currentUser.canvasSiteId).then(
    data => {
      grantingRoles.value = data.grantingRoles
      selectedRole.value = data.grantingRoles[0]
      sections.value = data.courseSections || []
      sectionSelected.value = sections.value.length ? sections.value[0] : null
      showSearchForm.value = true
    },
    showUnauthorized
  ).catch(() => showUnauthorized()
  ).finally(() => contextStore.loadingComplete())
})

const hideAlert = alertName => {
  messages[alertName] = null
  alertScreenReader('Alert hidden')
  putFocusNextTick('page-title')
}

const resetForm = () => {
  searchText.value = ''
  searchType.value = 'name'
  searchTypeNotice.value = ''
  selectedRole.value = grantingRoles.value[0]
  sectionSelected.value = sections.value.length ? sections.value[0] : null
}

const resetImportState = () => {
  userAdded.value = false
  messages.additionSuccessMessage = false
}

const resetSearchState = () => {
  messages.errorStatus = null
  messages.noUserSelectedAlert = false
  messages.searchAlert = null
  selectedUser.value = null
  showUsersArea.value = false
  userSearchResults.value = []
  userSearchResultsCount.value = 0
}

const showErrorStatus = message => {
  messages.errorStatus = message
}

const showSearchAlert = message => {
  messages.searchAlert = message
}

const showUnauthorized = () => {
  showErrorStatus('Authorization check failed.')
  contextStore.loadingComplete()
}

const srFriendlyRole = role => {
  return role === 'TA' || role === 'Lead TA' ? replace(role, 'TA', 'T A') : role
}

const uidForScreenReader = uid => {
  return String(uid || '').split('').join(' ')
}

const startOver = () => {
  alertScreenReader('Starting a new search.')
  resetForm()
  resetSearchState()
  resetImportState()
  putFocusNextTick('radio-btn-name')
}

const submitSearch = () => {
  resetSearchState()
  resetImportState()
  if (!trim(searchText.value)) {
    showSearchAlert('You did not enter any search terms.')
    putFocusNextTick('search-text')
  } else if (searchType.value === 'uid' && !isFinite(searchText.value)) {
    showSearchAlert('UID search terms must be numeric.')
    putFocusNextTick('search-text')
  } else {
    alertScreenReader('Loading person search results.')
    showUsersArea.value = true
    isSearching.value = true
    const searchTimer = setInterval(() => {
      alertScreenReader('Still searching.')
    }, 7000)
    searchUsers(searchText.value, searchType.value).then(data => {
      userSearchResults.value = data.users
      if (data.users && data.users.length) {
        userSearchResultsCount.value = data.users[0].resultCount
        selectedUser.value = data.users[0]
      } else {
        userSearchResultsCount.value = 0
        let noResultsAlert = 'Your search did not match anyone with a CalNet ID.'
        if (searchType.value === 'uid') {
          noResultsAlert += ' CalNet UIDs must be an exact match.'
        }
        showSearchAlert(noResultsAlert)
      }
    }, () => {
      showErrorStatus('Person search failed.')
      showSearchForm.value = true
    }).finally(() => {
      clearInterval(searchTimer)
      isSearching.value = false
      if (userSearchResults.value.length) {
        putFocusNextTick('person-search-results-caption')
      } else if (messages.searchAlert) {
        putFocusNextTick('search-text')
      } else {
        putFocusNextTick('add-user-submit-search-btn')
      }
    })
  }
}

const submitUser = () => {
  isAddingUser.value = true
  alertScreenReader(`Adding ${selectedUserFullName.value} with role ${srFriendlyRole(selectedRole.value)}.`)
  const addUserTimer = setInterval(() => {
    alertScreenReader('Still processing.')
  }, 7000)
  const sectionId = sectionSelected.value ? sectionSelected.value.id : null
  addUser(
    contextStore.currentUser.canvasSiteId,
    selectedUser.value.uid,
    sectionId,
    selectedRole.value
  ).then(
    data => {
      const sectionName = sectionSelected.value ? get(find(sections.value, {'id': data.sectionId}), 'name', sectionSelected.value.name) : null
      userAdded.value = {
        ...data.userAdded,
        fullName: selectedUserFullName.value,
        role: data.role,
        sectionName
      }
      alertScreenReader('success', 'assertive')
      resetSearchState()
      resetForm()
      messages.additionSuccessMessage = true
      putFocusNextTick('success-message')
    },
    error => {
      alertScreenReader('Error', 'assertive')
      messages.errorStatus = error || 'Request to add person failed'
      showUsersArea.value = true
      putFocusNextTick('add-user-btn')
    }
  ).catch(
    error => {
      messages.errorStatus = error || 'Request to add person failed'
      showUsersArea.value = true
      putFocusNextTick('add-user-btn')
    }
  ).finally(
    () => {
      clearInterval(addUserTimer)
      isAddingUser.value = false
      showSearchForm.value = true
      iframeScrollToTop()
    }
  )
}
</script>

<style scoped lang="scss">
.add-user-submit-search-btn-container {
  margin-right: auto;
  margin-left: 0.125rem;
  min-width: 10rem;
  width: 100%;
}
.search-text-field {
  flex: 1 1 66%;
  margin-right: 0.25rem;
  min-width: 12rem;
}
.select-user-radio :deep(.v-label) {
  font-size: 0.875rem;
  margin-left: 0.125rem;
  word-break: normal;
}
@media screen and (max-width: 992px) {
  table {
    border-collapse: collapse;
     thead {
      border: 0;
      clip: rect(0 0 0 0);
      height: 1px;
      margin: -1px;
      overflow: hidden;
      padding: 0;
      position: absolute;
      width: 1px;
    }
    tbody tr {
      border: 0;
      display: block;
      width: 100%;
      &:last-child {
        border-bottom: 1pt solid rgba(var(--v-border-color), var(--v-border-opacity));
      }
      td {
        border: 0;
        display: block;
        padding: 2px 4px !important;
        width: 100%;
        &::before {
          content: attr(data-label);
          float: left;
          font-weight: bold;
          margin-right: 1rem;
          opacity: var(--v-medium-emphasis-opacity);
          width: 6rem;
        }
        &:not(:first-child) {
          padding: 4px 2rem !important;
          &:last-child {
            padding-bottom: 8px !important;
          }
        }
      }
    }
  }
}
</style>
