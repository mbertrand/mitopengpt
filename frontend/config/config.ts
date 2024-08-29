import { Settings, Limits } from "@/types/settings"

export const SEARCH_ENDPOINT = process.env.NEXT_PUBLIC_SEARCH_ENDPOINT
export const CHAT_ENDPOINT = process.env.NEXT_PUBLIC_CHAT_ENDPOINT
export const CHAT_MODEL = process.env.CHAT_MODEL || 'gpt-4o'
export const IS_PRODUCTION = process.env.NODE_ENV === "production"

export const DEFAULT_USER_PROMPT = "Answer the following question, using ONLY the course information provided below. \
Never use any other sources for your answer."
export const DEFAULT_SYSTEM_PROMPT = "You answer questions based on information from MIT courses, in the style of a friendly professor."

export const DEFAULT_SETTINGS: Settings = {
  mode: "2",
  results: "5",
  sentences: "medium",
  threshold: "0.5",
  chat_model: CHAT_MODEL,
  api_key: "", // pragma: allowlist secret
  systemPrompt: DEFAULT_SYSTEM_PROMPT,
  userPrompt: DEFAULT_USER_PROMPT
}

export const DEFAULT_LIMITS: Limits = {
  results_max: 20,
  results_min: 1,
}
