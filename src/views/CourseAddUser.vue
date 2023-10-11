<template>
  <div v-if="!isLoading" class="page-course-add-user">
    <MaintenanceNotice course-action-verb="person is added" />
    <Header1 text="Find a Person to Add" />
    <div>
      <v-row
        v-if="showAlerts"
        id="alerts-container"
        role="alert"
        tabindex="-1"
      >
        <v-col md="12">
          <div v-if="errorStatus" class="alert alert-error page-course-add-user-alert">
            <div class="d-flex align-center">
              <v-icon icon="mdi-alert" class="canvas-notice-icon mr-2" />
              {{ errorStatus }}
            </div>
            <div class="alert-close-button-container d-flex ml-4">
              <button
                id="hide-search-error-button"
                class="align-self-center"
                @click="errorStatus = ''"
              >
                <v-icon icon="mdi-close-circle" />
                <span class="sr-only">Hide Alert</span>
              </button>
            </div>
          </div>
          <div v-if="noUserSelectedAlert" class="alert alert-error page-course-add-user-alert">
            Please select a person from the search results.
            <div class="alert-close-button-container d-flex ml-4">
              <button
                id="hide-select-user-alert-button"
                class="align-self-center"
                @click="noUserSelectedAlert = ''"
              >
                <v-icon icon="mdi-close-circle" />
                <span class="sr-only">Hide Alert</span>
              </button>
            </div>
          </div>
          <div v-if="searchAlert" class="alert alert-error page-course-add-user-alert">
            {{ searchAlert }}
            {{ searchTypeNotice }}
            Please try again.
            <div class="alert-close-button-container d-flex ml-4">
              <button
                id="hide-search-alert-button"
                class="align-self-center"
                @click="searchAlert = null"
              >
                <v-icon icon="mdi-close-circle" />
                <span class="sr-only">Hide Alert</span>
              </button>
            </div>
          </div>
          <div v-if="userSearchResultsCount > userSearchResults.length" class="alert alert-info page-course-add-user-alert">
            Your search returned {{ userSearchResultsCount }} results, but only the first
            {{ userSearchResults.length }} are shown.
            Please refine your search to limit the number of results.
          </div>
          <div v-if="userSearchResultsCount && (userSearchResultsCount === userSearchResults.length)" class="sr-only">
            {{ userSearchResultsCount }} search results loaded.
          </div>
          <div
            v-if="additionSuccessMessage"
            id="success-message"
            class="alert alert-success page-course-add-user-alert"
          >
            {{ userAdded.fullName }} was added to the
            &ldquo;{{ userAdded.sectionName }}&rdquo; section of this course as a {{ userAdded.role }}.
            <div class="alert-close-button-container d-flex ml-4">
              <button
                id="hide-search-success-button"
                class="align-self-center"
                @click="additionSuccessMessage = false"
              >
                <v-icon icon="mdi-close-circle" />
                <span class="sr-only">Hide Alert</span>
              </button>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row v-if="showSearchForm" no-gutters>
        <v-col>
          <form @submit.prevent="searchUsers">
            <v-row class="horizontal-form" no-gutters>
              <v-col cols="12" sm="6" class="d-flex align-center my-1 pr-sm-3">
                <label for="search-type" class="text-no-wrap mt-0 pr-3">Search By</label>
                <select
                  id="search-type"
                  v-model="searchType"
                  class="d-flex align-center mb-0"
                  :disabled="isSearching"
                  @change="updateSearchTextType"
                >
                  <option value="name">Last Name, First Name</option>
                  <option value="email">Email</option>
                  <option value="uid" aria-label="CalNet U I D">CalNet UID</option>
                </select>
              </v-col>
              <v-col cols="12" sm="4" class="d-flex align-center my-1 pr-sm-3">
                <input
                  id="search-text"
                  v-model="searchText"
                  :aria-label="`enter search terms. search by ${searchType === 'uid' ? 'CalNet U I D' : searchType}`"
                  class="mb-0"
                  :disabled="isSearching"
                  :type="searchTextType"
                >
              </v-col>
              <v-col cols="12" sm="2" class="column-align-center d-flex align-center my-1">
                <v-btn
                  id="add-user-submit-search-btn"
                  color="primary"
                  type="submit"
                  :disabled="!searchText || isSearching"
                  class="w-100"
                  aria-label="Submit search"
                >
                  <span v-if="!isSearching">Go</span>
                  <span v-if="isSearching">
                    <SpinnerWithinButton /> Searching...
                  </span>
                </v-btn>
              </v-col>
            </v-row>
          </form>
        </v-col>
      </v-row>
      <v-row v-if="showSearchForm" no-gutters>
        <v-col md="12">
          <div class="shrink icon-blue">
            <v-btn
              id="add-user-help-btn"
              aria-controls="page-help-notice"
              aria-haspopup="true"
              :aria-expanded="`${toggle.displayHelp}`"
              class="font-weight-regular text-no-wrap my-2"
              prepend-icon="mdi-help-circle"
              variant="text"
              @click="toggle.displayHelp = !toggle.displayHelp"
            >
              Need help finding someone?
            </v-btn>
          </div>
          <v-expand-transition>
            <v-card
              v-show="toggle.displayHelp"
              id="page-help-notice"
              class="user-search-notice rounded-0 mx-8 mb-4"
              elevation="0"
            >
              <!-- Note: This help text content is also maintained in the canvas-customization.js script -->
              <dl class="user-search-notice-description-list">
                <dt class="user-search-notice-description-term">UC Berkeley Faculty, Staff and Students</dt>
                <dd class="user-search-notice-description">
                  UC Berkeley faculty, staff and students <em>(regular and concurrent enrollment)</em> can be found in the
                  <OutboundLink href="http://directory.berkeley.edu/">CalNet Directory</OutboundLink>
                  and be added to your site using their CalNet UID or official email address.
                </dd>
                <dt class="user-search-notice-description-term">Guests</dt>
                <dd class="user-search-notice-description">
                  Peers from other institutions or guests from the community must be sponsored with a
                  <OutboundLink href="https://idc.berkeley.edu/guests/">CalNet Guest Account.</OutboundLink>
                  Do NOT request a CalNet Guest Account for concurrent enrollment students.
                </dd>
                <dt class="user-search-notice-description-term">More Information</dt>
                <dd class="user-search-notice-description">
                  Go to this
                  <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0010842">bCourses help page</OutboundLink>
                  for more information about adding people to bCourses sites.
                </dd>
              </dl>
            </v-card>
          </v-expand-transition>
        </v-col>
      </v-row>
      <v-row v-if="showUsersArea" no-gutters>
        <h2 id="user-search-results-header" class="sr-only" tabindex="-1">Person Search Results. Sorted by last name.</h2>
        <v-col v-if="userSearchResults.length > 0" md="12">
          <table class="table table-striped">
            <caption class="sr-only">Select the person you wish to add to the course site</caption>
            <thead>
              <tr>
                <th scope="col"><span class="sr-only">Actions</span></th>
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
                <td :id="`user-search-result-row-select-${index}`" class="px-3 py-4">
                  <input
                    :id="`user-search-result-input-${index}`"
                    v-model="selectedUser"
                    type="radio"
                    name="selectedUser"
                    :value="user"
                    :aria-labelled-by="`user-search-result-row-name-${index} user-search-result-row-ldap-uid-${index}`"
                  >
                </td>
                <td :id="`user-search-result-row-name-${index}`" class="px-3 py-4">
                  <label :for="`user-search-result-input-${index}`" class="form-input-label-no-align">
                    {{ user.firstName }} {{ user.lastName }}
                  </label>
                </td>
                <td :id="`user-search-result-row-ldap-uid-${index}`" class="px-3 py-4">
                  {{ user.uid }}
                </td>
                <td :id="`user-search-result-row-email-${index}`" class="px-3 py-4">
                  {{ user.emailAddress }}
                </td>
              </tr>
            </tbody>
          </table>
          <v-row no-gutters>
            <v-col>
              <v-row no-gutters class="my-2">
                <v-col
                  cols="2"
                  offset-sm="2"
                  offset-md="4"
                  class="d-flex align-center justify-end pr-3"
                >
                  <label for="user-role"><strong>Role</strong></label>
                </v-col>
                <v-col cols="10" sm="8" md="6">
                  <select id="user-role" v-model="selectedRole">
                    <option v-for="role in grantingRoles" :key="role" :value="role">
                      <template v-if="role === 'TA' || role === 'Lead TA'">
                        {{ replace(role, 'TA', 'T&ZeroWidthSpace;A') }}
                      </template>
                      <template v-else>{{ role }}</template>
                    </option>
                  </select>
                </v-col>
              </v-row>
              <v-row no-gutters class="mb-2">
                <v-col
                  cols="2"
                  offset-sm="2"
                  offset-md="4"
                  class="d-flex align-center justify-end pr-3"
                >
                  <label for="course-section"><strong>Section</strong></label>
                </v-col>
                <v-col cols="10" sm="8" md="6">
                  <select id="course-section" v-model="selectedSection">
                    <option v-for="section in courseSections" :key="section.name" :value="section">
                      {{ section.name }}
                    </option>
                  </select>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col md="12">
              <div class="d-flex justify-end">
                <v-btn
                  id="add-user-btn"
                  class="mx-1"
                  color="primary"
                  :disabled="!selectedUser"
                  @click="submitUser"
                >
                  Add Person
                </v-btn>
                <v-btn
                  id="start-over-btn"
                  class="mx-1"
                  @click="startOver"
                >
                  Start Over
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Header1 from '@/components/utils/Header1.vue'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'
import OutboundLink from '@/components/utils/OutboundLink'
import SpinnerWithinButton from '@/components/utils/SpinnerWithinButton.vue'
import {addUser, getAddUserOptions, searchUsers} from '@/api/canvas-user'
import {iframeScrollToTop, putFocusNextTick} from '@/utils'
import {find, get, replace, trim} from 'lodash'

export default {
  name: 'CourseAddUser',
  components: {Header1, MaintenanceNotice, OutboundLink, SpinnerWithinButton},
  mixins: [Context],
  data: () => ({
    additionSuccessMessage: false,
    courseSections: [],
    errorStatus: null,
    grantingRoles: [],
    isSearching: false,
    noUserSelectedAlert: null,
    searchAlert: null,
    searchText: null,
    searchTextType: 'text',
    searchType: 'name',
    searchTypeNotice: null,
    selectedRole: null,
    selectedSection: null,
    selectedUser: null,
    showAlerts: null,
    showSearchForm: null,
    showUsersArea: null,
    toggle: {
      displayHelp: false
    },
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
      response => {
        this.grantingRoles = response.grantingRoles
        this.selectedRole = response.grantingRoles[0]
        this.courseSections = response.courseSections
        this.selectedSection = response.courseSections[0]
        this.showSearchForm = true
      },
      this.showUnauthorized
    ).catch(this.showUnauthorized
    ).finally(() => {
      this.$ready()
    })
  },
  methods: {
    replace,
    resetForm() {
      this.searchTextType = 'text'
      this.searchText = ''
      this.searchType = 'name'
      this.searchTypeNotice = ''
      this.selectedRole = this.grantingRoles[0]
      this.selectedSection = this.courseSections[0]
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
    searchUsers() {
      this.resetSearchState()
      this.resetImportState()
      if (!trim(this.searchText)) {
        this.showSearchAlert('You did not enter any search terms.')
      } else if (this.searchType === 'uid' && !isFinite(this.searchText)) {
        this.showSearchAlert('UID search terms must be numeric.')
      } else {
        this.alertScreenReader('Loading person search results')
        this.showUsersArea = true
        this.isSearching = true
        searchUsers(this.searchText, this.searchType).then(response => {
          this.userSearchResults = response.users
          if (response.users && response.users.length) {
            this.userSearchResultsCount = response.users[0].resultCount
            this.selectedUser = response.users[0]
            this.$ready('user-search-results-header')
          } else {
            this.userSearchResultsCount = 0
            let noResultsAlert = 'Your search did not match anyone with a CalNet ID.'
            if (this.searchType === 'uid') {
              noResultsAlert += ' CalNet UIDs must be an exact match.'
            }
            this.showSearchAlert(noResultsAlert)
            this.$ready('alerts-container')
          }
          this.showAlerts = true
        }, () => {
          this.showErrorStatus('Person search failed.')
          this.showSearchForm = true
          this.$ready('alerts-container')
        }).finally(() => this.isSearching = false)
      }
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
      this.$ready('alerts-container')
    },
    startOver() {
      this.showAlerts = false
      this.alertScreenReader('Starting a new search.')
      this.resetForm()
      this.resetSearchState()
      this.resetImportState()
      putFocusNextTick('search-type')
    },
    submitUser() {
      this.loadingStart()
      iframeScrollToTop()
      this.showUsersArea = false
      this.showSearchForm = false
      this.alertScreenReader(`Adding ${this.selectedUserFullName} with role ${this.selectedRole}`)
      this.showAlerts = true
      addUser(this.currentUser.canvasSiteId, this.selectedUser.uid, this.selectedSection.id, this.selectedRole).then(response => {
        this.userAdded = {
          ...response.userAdded,
          fullName: this.selectedUserFullName,
          role: response.role,
          sectionName: get(find(this.courseSections, {'id': response.sectionId}), 'name', this.selectedSection.name)
        }
        this.resetSearchState()
        this.resetForm()
        this.additionSuccessMessage = true
      }, () => {
        this.errorStatus = 'Request to add person failed'
        this.showUsersArea = true
      }).catch(() => {
        this.errorStatus = 'Request to add person failed'
        this.showUsersArea = true
      }).finally(() => {
        this.showSearchForm = true
        this.$ready('alerts-container')
      })
    },
    updateSearchTextType() {
      this.searchTextType = (this.searchType === 'uid') ? 'number' : 'text'
    }
  }
}
</script>

<style scoped lang="scss">
.page-course-add-user {
  background: $color-white;
  padding: 10px;
  .page-course-add-user-alert {
    display: flex;
    font-weight: 500;
    justify-content: space-between;
    margin-bottom: 20px;
  }
  .user-search-notice {
    border: 1px solid #d0d0d0;
    padding: 15px;
    .user-search-notice-description-list {
      margin-bottom: 0;
    }
    .user-search-notice-description-term {
      font-weight: bold;
      margin: 5px 0;
    }
    .user-search-notice-description {
      margin-left: 15px;
    }
  }
  .column-align-center {
    text-align: center;
  }
}
</style>
