<script>
import _ from 'lodash'
import Utils from '@/mixins/Utils'
import {useContextStore} from '@/stores/context'

export default {
  name: 'CanvasUtils',
  mixins: [Utils],
  methods: {
    getCanvasCourseId() {
      const idParam = this.$_.get(this.$route, 'params.id')
      if (idParam) {
        this.canvasCourseId = this.toInt(idParam)
      } else {
        this.canvasCourseId = 'embedded'
      }
    },
    isCanvasCourseIdValid(canvasCourseId) {
      canvasCourseId = _.trim(canvasCourseId)
      return !!canvasCourseId
        && canvasCourseId.match(/^\d+$/)
        && parseInt(canvasCourseId, 10) <= useContextStore().config.maxValidCanvasCourseId
    }
  }
}
</script>
