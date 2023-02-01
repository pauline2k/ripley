<script>
import { mapActions } from 'pinia'
import { mapState } from 'pinia'
import { useContextStore } from "@/stores/context"

export default {
  name: 'Context',
  computed: {
    ...mapState(useContextStore, ['loading']),
  },
  methods: {
    ...mapActions(useContextStore, [
      'loadingComplete',
      'loadingStart'
    ])
  }
}
</script>
