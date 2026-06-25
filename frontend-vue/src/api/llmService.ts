/**
 * LLM Service - OpenAI-compatible API client
 * Supports: OpenAI, DeepSeek, Qwen (通义千问), Zhipu (智谱AI), custom providers
 *
 * Design doc ref: M8 LLM结构化研判
 * Architecture: Frontend calls backend /api/llm/* proxy, or direct provider API for testing
 */

export interface LLMConfig {
  provider: string
  endpoint: string
  apiKey: string
  model: string
  temperature: number
  maxTokens: number
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface ChatCompletionRequest {
  messages: ChatMessage[]
  temperature?: number
  max_tokens?: number
  stream?: boolean
  response_format?: { type: 'json_object' | 'text' }
}

export interface ChatCompletionResponse {
  id: string
  model: string
  choices: {
    index: number
    message: { role: string; content: string }
    finish_reason: string
  }[]
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

export interface LLMTestResult {
  success: boolean
  latencyMs: number
  model: string
  provider: string
  response?: string
  error?: string
  usage?: { prompt_tokens: number; completion_tokens: number; total_tokens: number }
}

/** Read config from localStorage */
export function getLLMConfig(): LLMConfig {
  return {
    provider: localStorage.getItem('llm_provider') || 'openai',
    endpoint: localStorage.getItem('llm_endpoint') || 'https://api.openai.com/v1',
    apiKey: localStorage.getItem('llm_api_key') || '',
    model: localStorage.getItem('llm_model') || 'gpt-4o',
    temperature: Number(localStorage.getItem('llm_temperature') || '0.3'),
    maxTokens: Number(localStorage.getItem('llm_max_tokens') || '2048'),
  }
}

/** Check if LLM is configured (has API key) */
export function isLLMConfigured(): boolean {
  const config = getLLMConfig()
  return config.apiKey.length > 0 && config.endpoint.length > 0
}

/** Get provider-specific chat endpoint */
function getChatEndpoint(config: LLMConfig): string {
  const base = config.endpoint.replace(/\/+$/, '')
  if (config.provider === 'zhipu') {
    return base + '/chat/completions'
  }
  return base + '/chat/completions'
}

/** Build headers for provider */
function getHeaders(config: LLMConfig): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (config.provider === 'zhipu') {
    headers['Authorization'] = 'Bearer ' + config.apiKey
  } else {
    headers['Authorization'] = 'Bearer ' + config.apiKey
  }
  return headers
}

/**
 * Send a chat completion request to the configured LLM provider
 */
export async function chatCompletion(
  messages: ChatMessage[],
  options?: Partial<ChatCompletionRequest>
): Promise<ChatCompletionResponse> {
  const config = getLLMConfig()
  if (!config.apiKey) {
    throw new Error('LLM API Key not configured. Go to Settings to configure.')
  }

  const body: Record<string, unknown> = {
    model: config.model,
    messages,
    temperature: options?.temperature ?? config.temperature,
    max_tokens: options?.max_tokens ?? config.maxTokens,
    stream: false,
  }

  if (options?.response_format) {
    body['response_format'] = options.response_format
  }

  const endpoint = getChatEndpoint(config)
  const headers = getHeaders(config)

  const resp = await fetch(endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })

  if (!resp.ok) {
    const errorText = await resp.text()
    let errorMsg = errorText
    try {
      const errJson = JSON.parse(errorText)
      errorMsg = errJson.error?.message || errJson.message || errorText
    } catch {}
    throw new Error(`LLM API error (${resp.status}): ${errorMsg}`)
  }

  return resp.json()
}

/**
 * Stream a chat completion (returns async generator)
 */
export async function* streamChatCompletion(
  messages: ChatMessage[],
  options?: Partial<ChatCompletionRequest>
): AsyncGenerator<string, void, unknown> {
  const config = getLLMConfig()
  if (!config.apiKey) {
    throw new Error('LLM API Key not configured.')
  }

  const body = {
    model: config.model,
    messages,
    temperature: options?.temperature ?? config.temperature,
    max_tokens: options?.max_tokens ?? config.maxTokens,
    stream: true,
  }

  const endpoint = getChatEndpoint(config)
  const headers = getHeaders(config)

  const resp = await fetch(endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })

  if (!resp.ok) {
    const errorText = await resp.text()
    throw new Error(`LLM API error (${resp.status}): ${errorText}`)
  }

  const reader = resp.body?.getReader()
  if (!reader) throw new Error('No response body')

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed || !trimmed.startsWith('data: ')) continue
      const data = trimmed.slice(6)
      if (data === '[DONE]') return
      try {
        const parsed = JSON.parse(data)
        const content = parsed.choices?.[0]?.delta?.content
        if (content) yield content
      } catch {}
    }
  }
}

/**
 * Test LLM connection with a simple chat completion
 */
export async function testLLMConnection(): Promise<LLMTestResult> {
  const config = getLLMConfig()
  const startTime = performance.now()

  try {
    if (!config.apiKey) {
      return {
        success: false,
        latencyMs: 0,
        model: config.model,
        provider: config.provider,
        error: 'API Key 未配置',
      }
    }

    const resp = await chatCompletion([
      { role: 'user', content: 'Hello, respond with just "OK".' }
    ], { max_tokens: 10, temperature: 0 })

    const latencyMs = Math.round(performance.now() - startTime)
    return {
      success: true,
      latencyMs,
      model: resp.model || config.model,
      provider: config.provider,
      response: resp.choices?.[0]?.message?.content || '',
      usage: resp.usage,
    }
  } catch (err: any) {
    const latencyMs = Math.round(performance.now() - startTime)
    return {
      success: false,
      latencyMs,
      model: config.model,
      provider: config.provider,
      error: err.message || String(err),
    }
  }
}

/**
 * Structured analysis prompt - per design doc M8
 * Sends risk assessment context to LLM for structured output
 */
export async function analyzeWithLLM(context: {
  event_summary: string
  risk_score: number
  current_stage: string
  risk_signals: Array<{ type: string; comment_id: string; text: string }>
  key_comments: string[]
  evidence: Array<{ title: string; content: string }>
}): Promise<ChatCompletionResponse> {
  const systemPrompt = `You are a campus opinion risk analyst. Analyze the following event and provide structured output in JSON format.

Event Summary: ${context.event_summary}
Risk Score: ${context.risk_score}
Current Stage: ${context.current_stage}

Key Risk Signals:
${context.risk_signals.map(s => `- [${s.type}] ${s.comment_id}: ${s.text}`).join('\n')}

Key Comments: ${context.key_comments.join(', ')}

Evidence:
${context.evidence.map(e => `- ${e.title}: ${e.content}`).join('\n')}

Provide a JSON response with:
{
  "risk_reason": "detailed risk analysis",
  "evolution_explanation": ["stage1 explanation", "stage2 explanation"],
  "key_comment_explanations": [{"comment_id": "...", "reason": "...", "risk_signal": "..."}],
  "intervention": {
    "official_statement": "...",
    "action_items": ["..."],
    "avoid_phrases": ["..."],
    "responsible_department": ["..."],
    "urgency": "..."
  },
  "human_review_required": true/false
}`

  return chatCompletion(
    [
      { role: 'system', content: 'You are a campus opinion risk analysis expert. Always respond in valid JSON.' },
      { role: 'user', content: systemPrompt }
    ],
    {
      temperature: 0.2,
      max_tokens: 4096,
      response_format: { type: 'json_object' },
    }
  )
}

// Default export for convenience
export default {
  getLLMConfig,
  isLLMConfigured,
  chatCompletion,
  streamChatCompletion,
  testLLMConnection,
  analyzeWithLLM,
}
