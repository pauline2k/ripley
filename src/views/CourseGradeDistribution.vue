<template>
  <div class="canvas-application pa-5">
    <div v-if="!isLoading">
      <h1 id="page-header" tabindex="-1">Grade Distribution</h1>
      {{ gradeDistribution }}
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {getGradeDistribution} from '@/api/canvas-site'

export default {
  name: 'CourseGradeDistribution',
  mixins: [Context],
  data: () => ({
    gradeDistribution: undefined,
  }),
  created() {
    this.loadingStart()
    getGradeDistribution(this.currentUser.canvasSiteId).then(
      data => {
        this.gradeDistribution = data
      }
    ).finally(() => this.$ready('Grade Distribution'))
  }
}
</script>
