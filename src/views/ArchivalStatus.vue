<template>
  <div v-if="!contextStore.isLoading" class="mx-10 my-5">
    <Header1 class="mb-4" text="View Course Retention Status" />
    <p class="my-4">
      The <OutboundLink href="https://rtl.berkeley.edu/services-programs/bcourses/bcourses-course-retention-policy">bCourses Course Retention Policy</OutboundLink> applies to all users of bCourses. bCourses sites for academic courses are retained for seven years after the end of the Academic Year in which the course was offered. Project Sites are subject to removal from the system if they do not have user activity for three years.
      <b v-if="feed.length">The chart below displays which of your courses and project sites are scheduled for removal from bCourses in June 2028.</b>
      <b v-if="!feed.length" id="archival-status-no-courses">You have no courses or project sites currently scheduled for removal.</b>
    </p>
    <p class="my-4">
      To learn how to preserve your work and student records or request an opt-out, review the <OutboundLink href="https://berkeley.service-now.com/kb?id=kb_article_view&sysparm_article=KB0012071">bCourses data retention policy knowledge base articles</OutboundLink>.
    </p>
    <div aria-live="polite">
      <v-alert
        v-if="error"
        id="archival-status-error"
        class="my-3"
        density="compact"
        role="none"
        :text="error"
        type="warning"
      />
    </div>
    <table v-if="feed.length" class="border-0 border-b-md border-t-md w-100">
      <caption class="sr-only">Course sites and their archival removal dates</caption>
      <thead class="bg-surface-light">
        <tr>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Course ID</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Course Code</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Course Name</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Role</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Term</th>
          <th class="font-weight-bold px-3 py-2 text-left" scope="col">Removal Date</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="item in feed"
          :id="`archival-status-row-${item.canvasSiteId}`"
          :key="item.canvasSiteId"
          class="border-0 border-t-sm"
        >
          <td class="px-3 py-2">
            <OutboundLink :id="`archival-status-site-id-${item.canvasSiteId}`" :href="item.url" no-wrap>{{ item.canvasSiteId }}</OutboundLink>
          </td>
          <td class="px-3 py-2">{{ item.courseCode }}</td>
          <td class="px-3 py-2">{{ item.name }}</td>
          <td :id="`archival-status-role-${item.canvasSiteId}`" class="px-3 py-2">{{ displayRole(item.currentUserRole) }}</td>
          <td class="px-3 py-2">{{ get(item, 'term.name') }}</td>
          <td :id="`archival-status-removal-date-${item.canvasSiteId}`" class="px-3 py-2">{{ removalDate(item) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import {get, sortBy} from 'lodash'
import Header1 from '@/components/utils/Header1.vue'
import OutboundLink from '@/components/utils/OutboundLink.vue'
import {getArchivalStatuses} from '@/api/canvas-site'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const error = ref()
const feed = ref()

onMounted(() => {
  getArchivalStatuses().then(
    data => {
      feed.value = sortBy(data, 'canvasSiteId')
    },
    e => {
      error.value = e
    }
  ).finally(() => contextStore.loadingComplete())
})

const roleDisplayMap: Record<string, string> = {
  'TaEnrollment': 'TA',
  'TeacherEnrollment': 'Teacher',
}

const displayRole = (role: string) => roleDisplayMap[role] || role

const removalDate = (item: any) => {
  // TODO: derive removal date from archivalTier once tier-to-date mapping is finalized
  return get(item, 'archivalStatus.optedOut') ? 'Exempt' : 'June 2028'
}
</script>
