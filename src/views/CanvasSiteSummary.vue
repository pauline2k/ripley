<template>
  <v-card v-if="!isLoading" id="mailing-list-details" elevation="3">
    <v-card-title>
      <div class="pl-1 pt-2">
        <h2>{{ canvasSite.name }}</h2>
        <div class="text-subtitle-2">
          <div>{{ canvasSite.sisCourseId }}</div>
          <div>
            <a
              :href="canvasSite.url"
              target="_blank"
              title="Open course site in new tab"
            >
              {{ canvasSite.url }}
            </a>
          </div>
        </div>
      </div>
    </v-card-title>
    <v-card-text>
      <div class="mt-3">
        <h3>Users</h3>
        <v-alert
          v-if="!config.isVueAppDebugMode && !currentUser.isAdmin"
          class="ma-2"
          :closable="true"
          density="compact"
          role="alert"
          type="info"
        >
          You must be an Admin user to "become" any one of the users below.
        </v-alert>
      </div>
      <v-container fluid>
        <v-row>
          <v-col cols="2">
            Canvas User ID
          </v-col>
          <v-col cols="2">
            UID
          </v-col>
          <v-col cols="2">
            Name
          </v-col>
          <v-col cols="4">
            Enrollments
          </v-col>
          <v-col cols="2">
          </v-col>
        </v-row>
        <v-row v-for="user in canvasSite.users" :key="user.id">
          <v-col class="text-no-wrap" cols="2">
            {{ user.id }}
          </v-col>
          <v-col class="text-no-wrap" cols="2">
            {{ user.uid }}
          </v-col>
          <v-col cols="2">
            <a
              :href="user.url"
              target="_blank"
              title="Open Canvas course user profile in new tab"
            >
              {{ user.sortableName }}
            </a>
          </v-col>
          <v-col cols="4">
            <ul>
              <li v-for="enrollment in user.enrollments" :key="enrollment.id">
                {{ describeEnrollment(enrollment) }}
              </li>
            </ul>
          </v-col>
          <v-col cols="2">
            <v-btn
              v-if="canBecomeAnotherUser() && isNumeric(user.uid)"
              :id="`become-${user.uid}`"
              variant="text"
              @click="devAuth(user.uid)"
            >
              <v-icon class="mr-2" icon="mdi-arrow-right-circle-outline" />
              Log in<span class="sr-only"> as {{ user.name }}</span>
            </v-btn>
            <div v-if="canBecomeAnotherUser() && user.uid && user.uid.includes('inactive')" class="text-red">
              <v-icon class="mr-2" icon="mdi-exclamation-circle" />
              <span class="sr-only"> as {{ user.name }} is </span>Inactive
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
import Context from '@/mixins/Context'
import {becomeUser} from '@/api/auth'
import {getCanvasSite} from '@/api/canvas-site'

export default {
  name: 'CanvasSiteSummary',
  mixins: [Context],
  data: () => ({
    canvasSite: undefined
  }),
  created() {
    const canvasSiteId = this.$_.get(this.$route, 'params.id')
    getCanvasSite(canvasSiteId, true).then(data => {
      this.canvasSite = data
      this.canvasSite.users = this.$_.sortBy(this.canvasSite.users, user => `${this.isNumeric(user.uid) ? '' : '_'} ${user.sortableName} ${user.uid}`)
      this.$ready()
    })
  },
  methods: {
    canBecomeAnotherUser() {
      return this.config.devAuthEnabled
        && (this.config.isVueAppDebugMode || this.currentUser.isAdmin)
        && this.currentUser.canvasSiteId
    },
    describeEnrollment(e) {
      let role
      switch(e.role) {
      case 'StudentEnrollment':
        role = 'Student'
        break
      case 'TaEnrollment':
        role = 'TA'
        break
      case 'TeacherEnrollment':
        role = 'Teacher'
        break
      default:
        role = e.role
      }
      return `${role} in ${e.sis_section_id}`
    },
    devAuth(uid) {
      becomeUser(this.currentUser.canvasSiteId, uid).then(() => window.location.href = '/')
    },
    isNumeric(s) {
      return /^\d+$/.test(s)
    }
  }
}
</script>
