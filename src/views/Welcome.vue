<template>
  <div class="ma-3">
    <h1>Hello {{ currentUser.firstName }}</h1>
    <div v-if="currentUser.isAdmin">
      <h2>Utilities</h2>
      <ul>
        <li><a href="/jobs">Jobs</a></li>
      </ul>
    </div>
    <h2>LTI tools, in standalone mode</h2>
    <ul>
      <li><a href="/canvas/course_add_user/:id">Find a User to Add</a></li>
      <li><a href="/canvas/course_grade_export/:id">E-Grade Export</a></li>
      <li><a href="/canvas/course_manage_official_sections/:id">Official Sections</a></li>
      <li><a href="/canvas/create_course_site">Create a Course Site</a></li>
      <li><a href="/canvas/create_project_site">Create a Project Site</a></li>
      <li><a href="/canvas/rosters/:id">bCourses Roster Photos</a></li>
      <li><a href="/canvas/site_creation">bCourses Site Creation</a></li>
      <li><a href="/canvas/site_mailing_list/:id">bCourses Mailing List</a></li>
      <li><a href="/canvas/site_mailing_lists">bCourses Site Mailing Lists</a></li>
      <li><a href="/canvas/user_provision">bCourses User Provision</a></li>
    </ul>
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'Welcome',
  mixins: [Context],
}
</script>
