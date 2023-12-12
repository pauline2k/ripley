<template>
  <div v-if="!isLoading" class="pb-5 px-5">
    <Header1 class="mb-0" text="Find a Person to Add" />
    <div class="my-2">
      <NeedHelpFindingSomeone v-if="showSearchForm" />
    </div>
    <MaintenanceNotice course-action-verb="person is added" />
    <div
      v-if="showAlerts"
      id="alerts-container"
      aria-live="polite"
      role="alert"
      tabindex="-1"
    >
      <div v-if="errorStatus" class="alert alert-error align-center d-flex font-weight-medium">
        <div class="pr-2">
          <v-icon class="canvas-notice-icon" :icon="mdiAlert" />
        </div>
        <div>
          {{ errorStatus }}
        </div>
        <div class="alert-close-button-container ml-auto">
          <button
            id="hide-search-error-button"
            @click="hideAlert('errorStatus')"
          >
            <v-icon :icon="mdiCloseCircle" />
            <span class="sr-only">Hide Alert</span>
          </button>
        </div>
      </div>
      <div v-if="noUserSelectedAlert" class="alert alert-error font-weight-medium">
        Please select a person from the search results.
        <div class="alert-close-button-container d-flex ml-4">
          <button
            id="hide-select-user-alert-button"
            class="align-self-center"
            @click="hideAlert('noUserSelectedAlert')"
          >
            <v-icon :icon="mdiCloseCircle" />
            <span class="sr-only">Hide Alert</span>
          </button>
        </div>
      </div>
      <div v-if="searchAlert" class="alert alert-error font-weight-medium">
        {{ searchAlert }}
        {{ searchTypeNotice }}
        Please try again.
        <div class="alert-close-button-container d-flex ml-4">
          <button
            id="hide-search-alert-button"
            class="align-self-center"
            @click="hideAlert('searchAlert')"
          >
            <v-icon :icon="mdiCloseCircle" />
            <span class="sr-only">Hide Alert</span>
          </button>
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
        v-if="additionSuccessMessage"
        id="success-message"
        class="alert alert-success font-weight-medium"
      >
        <span v-if="userAdded.sectionName">
          {{ userAdded.fullName }} was added to the &ldquo;{{ userAdded.sectionName }}&rdquo; section of this course
          as a <span aria-hidden="true">{{ userAdded.role }}.</span>
          <span class="sr-only">{{ srFriendlyRole(userAdded.role) }}.</span>
        </span>
        <span v-if="!userAdded.sectionName">
          {{ userAdded.fullName }} was added to the Canvas site as a <span aria-hidden="true">{{ userAdded.role }}.</span>
          <span class="sr-only">{{ srFriendlyRole(userAdded.role) }}.</span>
        </span>
        <div class="alert-close-button-container d-flex ml-4">
          <button
            id="hide-search-success-button"
            class="align-self-center"
            @click="hideAlert('additionSuccessMessage')"
          >
            <v-icon :icon="mdiCloseCircle" />
            <span class="sr-only">Hide Alert</span>
          </button>
        </div>
      </div>
    </div>
    <v-container fluid>
      <v-row v-if="showSearchForm" no-gutters>
        <v-col>
          <v-row justify="center" no-gutters>
            <v-col cols="12">
              <label for="search-type" class="text-subtitle-1">Search By</label>
              <v-radio-group
                id="search-type"
                v-model="searchType"
                color="primary"
                density="compact"
                :disabled="isSearching || isAddingUser"
                hide-details
              >
                <v-radio id="radio-btn-name" value="name">
                  <template #label>
                    <div class="pl-1 text-black text-body-2">Last Name, First Name</div>
                  </template>
                </v-radio>
                <v-radio id="radio-btn-email" value="email">
                  <template #label>
                    <div class="pl-1 text-black text-body-2">Email</div>
                  </template>
                </v-radio>
                <v-radio id="radio-btn-uid" value="uid">
                  <template #label>
                    <div class="pl-1 text-black text-body-2">CalNet UID</div>
                  </template>
                </v-radio>
              </v-radio-group>
              <div class="align-center d-flex py-3">
                <div class="pr-3">
                  <v-text-field
                    id="search-text"
                    v-model="searchText"
                    :aria-label="`enter search terms, search by ${searchType === 'uid' ? 'CalNet U I D' : searchType}`"
                    class="search-text-field"
                    density="comfortable"
                    :disabled="isSearching || isAddingUser"
                    hide-details
                    :placeholder="searchType === 'name' ? 'Last name, first name' : (searchType === 'uid' ? 'UID' : 'Email')"
                    variant="outlined"
                    @keydown.enter="submitSearch"
                  />
                </div>
                <div>
                  <v-btn
                    id="add-user-submit-search-btn"
                    aria-label="Submit search"
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
            <caption class="text-left font-weight-bold pl-3 py-2">
              Search Results
              <span class="sr-only">Sorted by last name. Select the person you wish to add to the course site using the radio button in column one.</span>
            </caption>
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col">Calnet UID</th>
                <th scope="col">Email</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(user, index) in userSearchResults"
                :id="`user-search-result-row-${index}`"
                :key="user.uid"
              >
                <td :id="`user-search-result-row-select-${index}`" class="d-flex align-center flex-nowrap px-3 py-4">
                  <input
                    :id="`user-search-result-input-${index}`"
                    v-model="selectedUser"
                    class="mr-4"
                    :disabled="isAddingUser"
                    name="selectedUser"
                    type="radio"
                    :value="user"
                    :aria-labelled-by="`user-search-result-row-name-${index} user-search-result-row-ldap-uid-${index}`"
                  >
                  <label :id="`user-search-result-row-name-${index}`" :for="`user-search-result-input-${index}`" class="form-input-label-no-align">
                    {{ user.firstName }} {{ user.lastName }}
                  </label>
                </td>
                <td :id="`user-search-result-row-ldap-uid-${index}`" class="px-3 py-4">
                  <span class="sr-only">Calnet U I D, </span>{{ user.uid }}
                </td>
                <td :id="`user-search-result-row-email-${index}`" class="px-3 py-4">
                  <span class="sr-only">Email, </span>{{ user.emailAddress }}
                </td>
              </tr>
            </tbody>
          </table>
          <v-row no-gutters>
            <v-col>
              <div class="pt-6 px-6">
                <div class="align-center d-flex">
                  <div :class="{'role-select-label': sections.length, 'pr-2': !sections.length}">
                    <label
                      aria-hidden="true"
                      class="text-subtitle-1"
                      for="user-role"
                    >
                      Role
                    </label>
                  </div>
                  <div class="ml-1">
                    <select
                      id="user-role"
                      v-model="selectedRole"
                      aria-label="Role"
                      :disabled="isAddingUser"
                    >
                      <option
                        v-for="role in grantingRoles"
                        :key="role"
                        :aria-label="srFriendlyRole(role)"
                        :value="role"
                      >
                        <span aria-hidden="true">{{ role }}</span>
                      </option>
                    </select>
                  </div>
                </div>
                <div v-if="sections.length" class="align-center d-flex pt-3">
                  <div class="role-select-label">
                    <label
                      aria-hidden="true"
                      class="text-subtitle-1"
                      for="course-section"
                    >
                      Section
                    </label>
                  </div>
                  <div class="ml-1">
                    <select
                      id="course-section"
                      v-model="sectionSelected"
                      aria-label="Section"
                      :disabled="isAddingUser"
                    >
                      <option v-for="section in sections" :key="section.name" :value="section">
                        {{ section.name }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col md="12">
              <div class="d-flex justify-end">
                <v-btn
                  id="add-user-btn"
                  class="mx-1"
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
                  class="mx-1"
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
import {mdiAlert, mdiCloseCircle} from '@mdi/js'
import {pluralize} from '@/utils'
</script>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'
import NeedHelpFindingSomeone from '@/components/utils/NeedHelpFindingSomeone'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton'
import {addUser, getAddUserOptions} from '@/api/canvas-user'
import {iframeScrollToTop, putFocusNextTick} from '@/utils'
import {find, get, replace, trim} from 'lodash'
import {searchUsers} from '@/api/user'

export default {
  name: 'CourseAddUser',
  components: {Header1, MaintenanceNotice, NeedHelpFindingSomeone, SpinnerWithinButton},
  mixins: [Context],
  data: () => ({
    additionSuccessMessage: false,
    errorStatus: undefined,
    grantingRoles: [],
    isAddingUser: false,
    isSearching: false,
    noUserSelectedAlert: undefined,
    searchAlert: undefined,
    searchText: undefined,
    searchType: 'name',
    searchTypeNotice: undefined,
    sections: [],
    sectionSelected: undefined,
    selectedRole: undefined,
    selectedUser: undefined,
    showAlerts: undefined,
    showSearchForm: undefined,
    showUsersArea: undefined,
    userAdded: {},
    userSearchResultsCount: 0,
    userSearchResults: [],
  }),
  computed: {
    selectedUserFullName() {
      return `${this.selectedUser.firstName} ${this.selectedUser.lastName}`
    }
  },
  created() {
    getAddUserOptions(this.currentUser.canvasSiteId).then(
      data => {
        this.grantingRoles = data.grantingRoles
        this.selectedRole = data.grantingRoles[0]
        this.sections = data.courseSections || []
        this.sectionSelected = this.sections.length ? this.sections[0] : null
        this.showSearchForm = true
      },
      this.showUnauthorized
    ).catch(() => this.showUnauthorized()
    ).finally(() => this.$ready())
  },
  methods: {
    hideAlert(alertName) {
      this.$data[alertName] = null
      this.alertScreenReader('Alert hidden')
      putFocusNextTick('page-title')
    },
    resetForm() {
      this.searchText = ''
      this.searchType = 'name'
      this.searchTypeNotice = ''
      this.selectedRole = this.grantingRoles[0]
      this.sectionSelected = this.sections.length ? this.sections[0] : null
    },
    resetImportState() {
      this.userAdded = false
      this.showAlerts = false
      this.additionSuccessMessage = false
    },
    resetSearchState() {
      this.errorStatus = null
      this.noUserSelectedAlert = false
      this.searchAlert = null
      this.selectedUser = null
      this.showUsersArea = false
      this.userSearchResults = []
      this.userSearchResultsCount = 0
    },
    showErrorStatus(message) {
      this.showAlerts = true
      this.errorStatus = message
    },
    showSearchAlert(message) {
      this.showAlerts = true
      this.searchAlert = message
    },
    showUnauthorized() {
      this.showErrorStatus('Authorization check failed.')
      this.$ready()
    },
    srFriendlyRole(role) {
      return role === 'TA' || role === 'Lead TA' ? replace(role, 'TA', 'T A') : role
    },
    startOver() {
      this.showAlerts = false
      this.alertScreenReader('Starting a new search.')
      this.resetForm()
      this.resetSearchState()
      this.resetImportState()
      putFocusNextTick('search-type')
    },
    submitSearch() {
      this.resetSearchState()
      this.resetImportState()
      if (!trim(this.searchText)) {
        this.showSearchAlert('You did not enter any search terms.')
      } else if (this.searchType === 'uid' && !isFinite(this.searchText)) {
        this.showSearchAlert('UID search terms must be numeric.')
      } else {
        this.alertScreenReader('Loading person search results.')
        this.showUsersArea = true
        this.isSearching = true
        let searchTimer = setInterval(() => {
          this.alertScreenReader('Still searching.')
        }, 7000)
        searchUsers(this.searchText, this.searchType).then(data => {
          this.userSearchResults = data.users
          if (data.users && data.users.length) {
            this.userSearchResultsCount = data.users[0].resultCount
            this.selectedUser = data.users[0]
          } else {
            this.userSearchResultsCount = 0
            let noResultsAlert = 'Your search did not match anyone with a CalNet ID.'
            if (this.searchType === 'uid') {
              noResultsAlert += ' CalNet UIDs must be an exact match.'
            }
            this.showSearchAlert(noResultsAlert)
          }
          this.showAlerts = true
        }, () => {
          this.showErrorStatus('Person search failed.')
          this.showSearchForm = true
        }).finally(() => {
          clearInterval(searchTimer)
          this.isSearching = false
          this.$ready('add-user-submit-search-btn')
        })
      }
    },
    submitUser() {
      this.isAddingUser = true
      this.showAlerts = true
      this.alertScreenReader(`Adding ${this.selectedUserFullName} with role ${this.srFriendlyRole(this.selectedRole)}.`)
      let addUserTimer = setInterval(() => {
        this.alertScreenReader('Still processing.')
      }, 7000)
      const sectionId = this.sectionSelected ? this.sectionSelected.id : null
      addUser(
        this.currentUser.canvasSiteId,
        this.selectedUser.uid,
        sectionId,
        this.selectedRole
      ).then(
        data => {
          const sectionName = this.sectionSelected ? get(find(this.sections, {'id': data.sectionId}), 'name', this.sectionSelected.name) : null
          this.userAdded = {
            ...data.userAdded,
            fullName: this.selectedUserFullName,
            role: data.role,
            sectionName
          }
          this.alertScreenReader('success', 'assertive')
          this.resetSearchState()
          this.resetForm()
          this.additionSuccessMessage = true
          putFocusNextTick('hide-search-success-button')
        },
        error => {
          this.alertScreenReader('Error', 'assertive')
          this.errorStatus = error || 'Request to add person failed'
          this.showUsersArea = true
          putFocusNextTick('add-user-btn')
        }
      ).catch(
        error => {
          this.errorStatus = error || 'Request to add person failed'
          this.showUsersArea = true
          putFocusNextTick('add-user-btn')
        }
      ).finally(
        () => {
          clearInterval(addUserTimer)
          this.isAddingUser = false
          this.showSearchForm = true
          iframeScrollToTop()
        }
      )
    }
  }
}
</script>

<style scoped lang="scss">
.role-select-label {
  width: 64px;
}
.search-text-field {
  width: 600px;
}
</style>
