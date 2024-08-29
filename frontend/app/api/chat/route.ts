import { OpenAIStream, StreamingTextResponse } from 'ai'
import { Configuration, OpenAIApi } from 'openai-edge'
import { getSettings } from '@/lib/settings'

// IMPORTANT! Set the runtime to edge
export const runtime = 'edge'

export async function POST(req: Request) {
  // Get User API Key
  const cachedKey = getSettings().api_key
  const api_key = (cachedKey === "") ? process.env.OPENAI_API_KEY : cachedKey
  const chat_model = getSettings().chat_model

  // Create an OpenAI API client (that's edge friendly!)
  const AI_CONFIG = new Configuration({
    apiKey: api_key
  })
  const openai = new OpenAIApi(AI_CONFIG)

  // Extract the `messages` from the body of the request
  const { messages } = await req.json()

  // Ask OpenAI for a streaming chat completion given the prompt
  const response = await openai.createChatCompletion({
    model: chat_model,
    temperature: 0,
    stream: true,
    messages
  })

  // Convert the response into a friendly text-stream
  const stream = OpenAIStream(response)

  // Respond with the stream
  return new StreamingTextResponse(stream)
}
