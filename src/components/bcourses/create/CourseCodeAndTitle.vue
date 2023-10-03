<template>
  <span>
    {{ course.courseCode }}<span v-if="course.title"> &mdash; {{ course.title }}</span>
    <span v-if="size(course.sections)">
      ({{ pluralize('section', course.sections.length, {0: 'No', 1: 'One'}) }})
    </span>
  </span>
</template>

<script lang="ts">
import {pluralize} from '@/utils'
import {size} from 'lodash'

export default {
  name: 'CourseCodeAndTitle',
  props: {
    course: {
      required: true,
      type: Object
    }
  },
  methods: {
    pluralize,
    size
  }
}
</script>
