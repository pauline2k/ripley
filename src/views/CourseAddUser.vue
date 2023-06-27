<template>
  <div class="canvas-application page-course-add-user">
    <MaintenanceNotice course-action-verb="user is added" />

    <h1 class="page-course-add-user-header">Find a Person to Add</h1>

    <div v-if="showError">
      <v-icon icon="mdi-exclamation-triangle" class="icon-red canvas-notice-icon" />
      {{ errorStatus }}
    </div>

    <div v-if="!showError">
      <v-row v-if="showAlerts" role="alert">
        <v-col v-if="!isLoading" md="12">
          <div v-if="noUserSelectedAlert" class="alert alert-error page-course-add-user-alert">
            Please select a user.
            <div class="alert-close-button-container">
              <button
                id="hide-select-user-alert-button"
                class="close-button"
                @click="noUserSelectedAlert = ''"
              >
                <v-icon icon="mdi-times-circle" />
                <span class="sr-only">Hide Alert</span>
              </button>
            </div>
          </div>

          <div v-if="searchAlert" class="alert alert-error page-course-add-user-alert">
            {{ searchAlert }}
            {{ searchTypeNotice }}
            Please try again.
            <div class="alert-close-button-container">
              <button
                id="hide-search-alert-button"
                class="close-button"
                @click="searchAlert = null"
              >
                <v-icon icon="mdi-times-circle" />
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
            {{ userSearchResultsCount }} user search results loaded.
          </div>

          <div v-if="additionSuccessMessage" id="success-message" class="alert alert-success page-course-add-user-alert">
            {{ userAdded.fullName }} was added to the
            &ldquo;{{ userAdded.sectionName }}&rdquo; section of this course as a {{ userAdded.role }}.
            <div class="alert-close-button-container">
              <button class="close-button" @click="additionSuccessMessage = ''">
                <v-icon icon="mdi-times-circle" />
                <span class="sr-only">Hide Alert</span>
              </button>
            </div>
          </div>

          <div v-if="additionFailureMessage" class="alert alert-error page-course-add-user-alert">
            <v-icon icon="mdi-exclamation-triangle" class="icon-red canvas-notice-icon" />
            {{ errorStatus }}
            <div class="alert-close-button-container">
              <button class="close-button" @click="additionFailureMessage = ''">
                <v-icon icon="mdi-times-circle" />
                <span class="sr-only">Hide Alert</span>
              </button>
            </div>
          </div>
        </v-col>
      </v-row>

      <v-row v-if="showSearchForm" no-gutters>
        <v-col md="6">
          <form class="canvas-page-form" @submit.prevent="searchUsers">
            <v-row class="horizontal-form" no-gutters>
              <v-col md="4">
                <label for="search-text" class="sr-only">Search users</label>
                <input
                  id="search-text"
                  v-model="searchText"
                  class="form-input-text"
                  :type="searchTextType"
                  placeholder="Find a person to add"
                >
              </v-col>
              <v-col md="6">
                <v-row no-gutters>
                  <v-col class="d-none d-sm-none d-md-block" md="2">
                    <label for="search-type" class="label label-horizontal form-entities">By:</label>
                  </v-col>
                  <v-col md="10">
                    <select
                      id="search-type"
                      v-model="searchType"
                      class="form-input-select"
                      @change="updateSearchTextType"
                    >
                      <option value="name">Last Name, First Name</option>
                      <option value="email">Email</option>
                      <option value="ldap_user_id" aria-label="CalNet U I D">CalNet UID</option>
                    </select>
                  </v-col>
                </v-row>
              </v-col>
              <v-col md="2" class="column-align-center">
                <button
                  id="submit-search"
                  type="submit"
                  :disabled="!searchText"
                  class="canvas-button canvas-button-primary full-wide"
                  aria-label="Perform User Search"
                >
                  Go
                </button>
              </v-col>
            </v-row>
          </form>
        </v-col>
      </v-row>

      <v-row v-if="showSearchForm" class="page-help-notice" no-gutters>
        <v-col md="12">
          <v-icon icon="mdi-question-circle" class="page-help-notice-icon left mr-2" />
          <div class="page-help-notice-left-margin">
            <button
              class="button-link"
              aria-controls="page-help-notice"
              aria-haspopup="true"
              :aria-expanded="`${toggle.displayHelp}`"
              @click="toggle.displayHelp = !toggle.displayHelp"
            >
              Need help finding someone?
            </button>
            <div aria-live="polite">
              <div v-if="toggle.displayHelp" id="page-help-notice" class="page-help-notice-content user-search-notice">
                <!-- Note: This help text content is also maintained in the public/canvas/canvas-customization.js script -->
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
                    <OutboundLink href="https://idc.berkeley.edu/guests/">CalNet Guest Account</OutboundLink>.
                    Do NOT request a CalNet Guest Account for concurrent enrollment students.
                  </dd>
                  <dt class="user-search-notice-description-term">More Information</dt>
                  <dd class="user-search-notice-description">
                    Go to this
                    <OutboundLink href="https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0010842">bCourses help page</OutboundLink>
                    for more information about adding people to bCourses sites.
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </v-col>
      </v-row>

      <v-progress-circular
        v-if="isLoading"
        class="mr-2"
        color="primary"
        indeterminate
      />

      <v-row v-if="showUsersArea" no-gutters>
        <h2 id="user-search-results-header" class="sr-only" tabindex="-1">User Search Results</h2>
        <v-col v-if="userSearchResults.length > 0" md="12">
          <form class="canvas-page-form">
            <fieldset class="form-fieldset">
              <legend class="sr-only">Select the user you wish to add to the course site:</legend>
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th scope="col"><span class="sr-only">Actions</span></th>
                    <th scope="col">Name</th>
                    <th scope="col">Calnet UID</th>
                    <th scope="col">Email</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(user, index) in userSearchResults" :id="`user-search-result-row-${index}`" :key="user.ldapUid">
                    <td :id="`user-search-result-row-select-${index}`">
                      <input
                        :id="`user-search-result-input-${index}`"
                        v-model="selectedUser"
                        type="radio"
                        name="selectedUser"
                        :value="user"
                        :aria-labelled-by="`user-search-result-row-name-${index} user-search-result-row-ldap-uid-${index}`"
                      >
                    </td>
                    <td :id="`user-search-result-row-name-${index}`">
                      <label :for="`user-search-result-${index}-input`" class="form-input-label-no-align">
                        {{ user.firstName }} {{ user.lastName }}
                      </label>
                    </td>
                    <td :id="`user-search-result-row-ldap-uid-${index}`">
                      {{ user.ldapUid }}
                    </td>
                    <td :id="`user-search-result-row-email-${index}`">
                      {{ user.emailAddress }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </fieldset>
            <v-row no-gutters>
              <v-col md="7">
                <v-row no-gutters>
                  <v-col sm="3">
                    <label for="user-role"><strong><span class="required-field-indicator">*</span> Role</strong>:</label>
                  </v-col>
                  <v-col sm="9">
                    <select id="user-role" v-model="selectedRole" class="form-input-select">
                      <option v-for="role in grantingRoles" :key="role" :value="role">
                        {{ role }}
                      </option>
                    </select>
                  </v-col>
                </v-row>
                <v-row no-gutters>
                  <v-col sm="3">
                    <label for="course-section"><strong><span class="required-field-indicator">*</span> Section</strong>:</label>
                  </v-col>
                  <v-col sm="9">
                    <select id="course-section" v-model="selectedSection" class="form-input-select">
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
                    class="canvas-button canvas-button-primary"
                    :disabled="!selectedUser"
                    @click="submitUser"
                  >
                    Add User
                  </v-btn>
                  <v-btn
                    id="start-over-btn"
                    class="canvas-button start-over-button"
                    @click="resetForm"
                  >
                    Start Over
                  </v-btn>
                </div>
              </v-col>
            </v-row>
          </form>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import MaintenanceNotice from '@/components/bcourses/shared/MaintenanceNotice'
import OutboundLink from '@/components/utils/OutboundLink'
import {addUser, getAddUserCourseSections, getCanvasSiteUserRoles, searchUsers} from '@/api/canvas-user'
import {iframeScrollToTop, putFocusNextTick} from '@/utils'

export default {
  name: 'CourseAddUser',
  components: {MaintenanceNotice, OutboundLink},
  mixins: [Context],
  data: () => ({
    additionFailureMessage: null,
    additionSuccessMessage: null,
    courseSections: [],
    errorStatus: null,
    grantingRoles: [],
    isLoading: null,
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
    showError: null,
    showSearchForm: null,
    showUsersArea: null,
    toggle: {
      displayHelp: false
    },
    userAdded: {},
    userSearchResultsCount: 0,
    userSearchResults: [],
  }),
  methods: {
    isAuthorized(response) {
      return (
        this.$_.includes(response.roleTypes, 'TeacherEnrollment') ||
        this.$_.includes(response.roleTypes, 'TaEnrollment') ||
        this.$_.includes(response.roles, 'globalAdmin')
      )
    },
    resetForm() {
      this.searchTextType = 'text'
      this.searchText = ''
      this.searchType = 'name'
      this.searchTypeNotice = ''
      this.showAlerts = false
      this.resetSearchState()
      this.resetImportState()
      putFocusNextTick('search-text')
    },
    resetImportState() {
      this.userAdded = false
      this.showAlerts = false
      this.additionSuccessMessage = false
      this.additionFailureMessage = false
    },
    resetSearchState() {
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
      if (!this.$_.trim(this.searchText)) {
        this.showSearchAlert('You did not enter any search terms.')
      } else if (this.searchType === 'ldap_user_id' && !isFinite(this.searchText)) {
        this.showSearchAlert('UID search terms must be numeric.')
      } else {
        this.$announcer.polite('Loading user search results')
        this.showUsersArea = true
        this.isLoading = true
        searchUsers(this.currentUser.canvasSiteId, this.searchText, this.searchType).then(response => {
          this.userSearchResults = response.users
          if (response.users && response.users.length) {
            this.userSearchResultsCount = response.users[0].resultCount
            this.selectedUser = response.users[0]
            putFocusNextTick('user-search-results-header')
          } else {
            this.userSearchResultsCount = 0
            let noResultsAlert = 'Your search did not match any users with a CalNet ID.'
            if (this.searchType === 'ldap_user_id') {
              noResultsAlert += ' CalNet UIDs must be an exact match.'
            }
            this.showSearchAlert(noResultsAlert)
          }
          this.isLoading = false
          this.showAlerts = true
          this.searchResultsFocus = true
        }, () => {
          this.showErrorStatus('User search failed.')
        })
      }
    },
    showErrorStatus(message) {
      this.isLoading = false
      this.showError = true
      this.errorStatus = message
    },
    showSearchAlert(message) {
      this.showAlerts = true
      this.searchAlert = message
      this.isLoading = false
    },
    showUnauthorized() {
      this.showErrorStatus('Authorization check failed.')
    },
    submitUser() {
      iframeScrollToTop()
      this.showUsersArea = false
      this.showSearchForm = false
      this.$announcer.polite('Adding user')
      this.isLoading = true
      this.showAlerts = true
      addUser(this.currentUser.canvasSiteId, this.selectedUser.ldapUid, this.selectedSection.id, this.selectedRole).then(response => {
        this.userAdded = {
          ...response.userAdded,
          fullName: this.selectedUser.firstName + ' ' + this.selectedUser.lastName,
          role: this.selectedRole,
          sectionName: this.selectedSection.name
        }
        this.additionSuccessMessage = true
        this.showSearchForm = true
        this.isLoading = false
        this.resetSearchState()
      }, () => {
        this.errorStatus = 'Request to add user failed'
        this.showSearchForm = true
        this.additionFailureMessage = true
        this.isLoading = false
        this.resetSearchState()
      })
    },
    updateSearchTextType() {
      this.searchTextType = (this.searchType === 'ldap_user_uid') ? 'number' : 'text'
    }
  },
  created() {
    this.isLoading = true
    getCanvasSiteUserRoles(this.currentUser.canvasSiteId).then(response => {
      if (this.isAuthorized(response)) {
        this.grantingRoles = response.grantingRoles
        this.selectedRole = response.grantingRoles[0]
        getAddUserCourseSections(this.currentUser.canvasSiteId).then(response => {
          this.isLoading = false
          this.courseSections = response.courseSections
          this.selectedSection = response.courseSections[0]
          this.showSearchForm = true
          this.$ready()
        }, this.showUnauthorized)
      } else {
        this.showUnauthorized()
      }
    }, this.showUnauthorized)
  }
}
</script>

<style scoped lang="scss">
.page-course-add-user {
  background: $color-white;
  padding: 10px;

  .page-course-add-user-alert {
    margin-bottom: 20px;
  }

  .page-course-add-user-header {
    color: $color-off-black;
    font-family: $body-font-family;
    font-size: 23px;
    font-weight: 400;
    line-height: 40px;
    margin: 8px 0;
  }

  button {
    &, &:hover, &:active, &:focus {
      font-family: $body-font-family;
      font-size: 14px;
      font-weight: 300;
    }
  }

  p {
    font-size: 14px;
    line-height: 16px;
    margin: 0 0 10px;
  }

  select {
    width: 100%;
  }

  .canvas-page-form {
    form input[type="text"] {
      font-family: $body-font-family;
      font-size: 14px;
      margin: 2px 10px 0 0;
      padding: 8px 12px;
    }

    .form-input-select {
      margin-bottom: 8px;
    }
  }

  .horizontal-form {
    .label {
      white-space: nowrap;
    }

    .label-horizontal {
      margin-top: 9px;
    }

    .form-entity {
      border: 1px solid $color-very-light-grey;
      font-family: Arial;
      font-size: 12px;
      height: 25px;
      margin: 3px 0;
      padding: 5px;
    }
  }

  .fa-black {
    color: $color-off-black !important;
  }

  .user-search-notice {
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

  @media #{$small-only} {
    .full-wide {
      width: 100%;
    }

    .horizontal-form {
      .columns {
        margin-bottom: 0;
      }
    }
  }
}
</style>
