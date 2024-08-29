export interface Settings {
  mode: string
  results: string
  sentences: string
  threshold: string
  api_key: string
  chat_model: string
  [key: string]: string
  systemPrompt: string
  userPrompt: string
}

export interface Limits {
  results_max: number
  results_min: number
  [key: string]: number
}
