export type Job = {
  id: number,
  disabled: boolean,
  key: string,
  schedule: JobSchedule,
  createdAt: string,
  updatedAt: string
}

export type JobSchedule = {
  type: string,
  value: object
}

export type Term = {
  id: number,
  name: string
}
