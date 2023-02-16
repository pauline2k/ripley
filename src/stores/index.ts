import {useContextStore} from '@/stores/context'

export default {
  setup() {
    return {
      store: useContextStore()
    }
  }
}
