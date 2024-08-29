import axios from "axios"
import { CHAT_ENDPOINT, SEARCH_ENDPOINT } from "config/config"

function createRequest(
  textareaValue: string,
  courseTitle: string,
  results: string,
  sentences: string,
  threshold: string,
  api_key: string,
  systemPrompt: string,
  userPrompt: string,
  chat_model: string
) {
  return api_key === "" ? {
    prompt: textareaValue,
    course: courseTitle,
    results: results,
    sentences: sentences,
    similarity_threshold: threshold,
    temperature: "0",
    systemPrompt: systemPrompt,
    userPrompt: userPrompt,
    chat_model: chat_model
  } : {
    prompt: textareaValue,
    course: courseTitle,
    results: results,
    sentences: sentences,
    similarity_threshold: threshold,
    temperature: "0",
    api_key: api_key,
    systemPrompt: systemPrompt,
    userPrompt: userPrompt,
    chat_model: chat_model
  }
}

export async function fetchData(
  textareaValue: string,
  courseTitle: string,
  mode: string,
  results: string,
  sentences: string,
  threshold: string,
  api_key: string,
  systemPrompt: string,
  userPrompt: string,
  chat_model: string
) {
  try {
    const url = mode === "1" ? SEARCH_ENDPOINT : CHAT_ENDPOINT
    const response = await axios.post(
      url || "",
      createRequest(textareaValue, courseTitle, results, sentences, threshold, api_key, systemPrompt, userPrompt, chat_model),
      {
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      }
    )
    return response.data
  } catch (err) {
    console.log(err)
    throw err
  }
}
