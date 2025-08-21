export type CanvasSite = {
  canvasSiteId: string,
  courseCode: string,
  name: string,
  officialSections: object[],
  url: string
}

export type Course = {
  id: number,
  courseCode: string,
  sections: Section[],
  slug: string,
  title: string
}

export interface HasCanvasSite {
  canvasSite: CanvasSite,
  teachingTerms: Semester[]
}

export interface HasJobStatus {
  jobId: number,
  jobStatus: string
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
  courseCode: string,
  courseSlug: string,
  isCourseSection: boolean,
  name: string,
  stagedState: string | undefined
}

export type Semester = {
  classes: Course[]
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
