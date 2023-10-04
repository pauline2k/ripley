<template>
  <div class="pa-8">
    <Header1 text="Manage Site Sections" />
    <div v-for="(courses, termId) in coursesByTerm" :key="termId">
      <h2>{{ getTermName(termId) }}</h2>
      <select
        id="course-sections"
        v-model="canvasSiteId"
      >
        <option :value="null">Choose...</option>
        <option
          v-for="course in courses"
          :key="course.canvasSiteId"
          :value="course.canvasSiteId"
        >
          {{ course.courseCode }} &mdash; {{ course.name }}
        </option>
      </select>
    </div>
  </div>
</template>

<script>
import Header1 from '@/components/utils/Header1'
import {defineComponent} from 'vue'
import {each} from 'lodash'
import {getTermName} from '@/utils'
import {myCurrentCanvasCourses} from '@/api/canvas-site'

export default defineComponent({
  name: 'ManageSites',
  components: {Header1},
  data: () => ({
    canvasSiteId: null,
    coursesByTerm: undefined
  }),
  watch: {
    canvasSiteId(value) {
      if (value) {
        this.$router.push({path: `/manage_official_sections/${value}`})
      }
    }
  },
  created() {
    this.coursesByTerm = {}
    myCurrentCanvasCourses().then(data => {
      each(data, (courses, term) => {
        if (courses.length) {
          this.coursesByTerm[term] = courses
        }
      })
      this.$ready()
    })
  },
  methods: {
    each,
    getTermName
  }
})
</script>
