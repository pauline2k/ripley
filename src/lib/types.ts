export type CanvasSite = {
  canvasSiteId: string,
  codeAndTerm: string,
  courseCode: string,
  name: string,
  officialSections: object[],
  term: Term,
  url: string
}

export type Course<T extends Section> = {
  id: number,
  courseCode: string,
  sections: T[],
  slug: string,
  title: string
}

export interface HasCanvasSite {
  canvasSite: CanvasSite,
  teachingTerms: Semester<Section>[]
}

export interface HasJobStatus {
  jobId: number,
  jobStatus: string
}

export type Instructor = {
  name: string,
  uid: string
}

export type Job = {
  id: number,
  disabled: boolean,
  jobStatus: string,
  key: string,
  schedule: JobSchedule,
  createdAt: string,
  updatedAt: string
}

export type JobRunSummary = {
  failed: boolean,
  finishedAt: string,
  jobKey: string,
  result: object,
  startedAt: string
}

export type JobSchedule = {
  type: string,
  value: object
}

export type Section = {
  id: number,
  canvasSites: CanvasSite[],
  courseCode: string,
  courseSlug: string,
  instructors: Instructor[],
  isCourseSection: boolean,
  name: string,
  schedules: {
    recurring: {
      schedule: {
        buildingName: string,
        roomNumber: string,
        schedule: string
      }
    }
  }
}

export type Semester<T extends Section> = {
  classes: Course<T>[]
}

export interface SectionEdit extends Section {
  nameDiscrepancy: boolean,
  selected: boolean,
  stagedState: string | undefined
}

export type ScreenReaderAlert = {
  message: string,
  politeness: string
}

export type SiteAuthorization = {
  authorizations: {
    canCreateCourseSite: boolean,
    canCreateProjectSite: boolean
  }
}

export type StandaloneToolOption = {
  disabled: boolean,
  icon: string,
  path: string,
  title: string
}

export type Term = {
  id: number,
  name: string
}
