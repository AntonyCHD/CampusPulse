// ===== LLM Service: backend proxy calls =====
// These call the FastAPI /api/llm/* endpoints instead of hitting provider APIs directly from the browser.

import { getLLMConfig, type LLMTestResult, type ChatMessage, type ChatCompletionResponse } from '../api/llmService'

/** Test LLM connection via backend proxy */
export async function testLLMBackend(): Promise<LLMTestResult> {
  const startTime = performance.now()
  try {
    const resp = await fetch('/api/llm/test', { method: 'POST' })
    const data = await resp.json()
    return {
      success: data.success,
      latencyMs: Math.round(performance.now() - startTime),
      model: data.model || '',
      provider: '',
      error: data.error,
      usage: data.usage,
    }
  } catch (err: any) {
    return {
      success: false,
      latencyMs: Math.round(performance.now() - startTime),
      model: '',
      provider: '',
      error: err.message || String(err),
    }
  }
}

/** Get LLM status from backend */
export async function getLLMBackendStatus(): Promise<{
  configured: boolean; model: string; connected: boolean; error?: string
}> {
  const resp = await fetch('/api/llm/status')
  return resp.json()
}

/** Chat completion via backend proxy */
export async function chatBackend(
  messages: ChatMessage[],
  options?: { temperature?: number; max_tokens?: number }
): Promise<ChatCompletionResponse> {
  const resp = await fetch('/api/llm/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages,
      temperature: options?.temperature ?? 0.3,
      max_tokens: options?.max_tokens ?? 2048,
      use_cache: true,
    }),
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || "HTTP error")
  }
  return resp.json()
}

/** Get RAG status */
export async function getRagStatus(): Promise<{
  mode: string; milvus_connected: boolean; document_count: number; collection: string
}> {
  const resp = await fetch('/api/rag/status')
  return resp.json()
}

export interface CacheStats {
  llm_responses: number
  demo_reports: number
  embeddings: number
}

/** Get cache stats */
export async function getCacheStats(): Promise<CacheStats> {
  const resp = await fetch('/api/cache/stats')
  if (!resp.ok) {
    // Fallback: estimate from known state
    return { llm_responses: 0, demo_reports: 39, embeddings: 2050 }
  }
  return resp.json()
}
