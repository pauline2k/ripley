export type Job = {
  id: number,
  disabled: boolean,
  key: string,
  schedule: JobSchedule,
  createdAt: string,
  updatedAt: string
}

export type JobHistory = {
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
