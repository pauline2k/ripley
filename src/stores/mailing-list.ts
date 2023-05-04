import {defineStore} from 'pinia'

export const useMailingListStore = defineStore('mailingList', {
  state: () => ({
    canvasSite: undefined,
    mailingList: undefined,
    updateSummary: undefined
  }),
  actions: {
    init() {
      this.canvasSite = this.mailingList = undefined
    },
    setCanvasSite(canvasSite: any) {
      const a = []
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
