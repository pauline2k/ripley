import {defineStore} from 'pinia'
import type {CanvasSite} from '@/lib/types'

export const useMailingListStore = defineStore('mailingList', {
  state: () => ({
    canvasSite: undefined as CanvasSite|undefined,
    mailingList: undefined,
    updateSummary: undefined
  }),
  actions: {
    init() {
      this.canvasSite = this.mailingList = this.updateSummary = undefined
    },
    setCanvasSite(canvasSite: CanvasSite) {
      const a: string[] = []
      if (canvasSite.courseCode !== canvasSite.name) {
        a.push(canvasSite.courseCode)
      }
      if (canvasSite.term && canvasSite.term.name) {
        a.push(canvasSite.term.name)
      }
      canvasSite.codeAndTerm = a.join(', ')
      this.canvasSite = canvasSite
    },
    setMailingList(mailingList: any) {
      this.mailingList = mailingList
      if (this.mailingList) {
        this.setCanvasSite(mailingList.canvasSite)
      }
    },
    setUpdateSummary(updateSummary: any) {
      this.updateSummary = updateSummary
    }
  }
})
