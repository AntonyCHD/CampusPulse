import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 120000
})

export interface Event {
  event_id: string
  event_type: string
  title: string
  comment_count: number
  like_count: number
  created_at: string
  risk_level?: string
  risk_score?: number
}

export interface RiskTrendPoint {
  date: string
  avg_risk_score: number
  event_count: number
}

export interface DashboardSummary {
  total_events: number
  today_events: number
  high_risk_events: number
  risk_distribution: Record<string, number>
  event_type_distribution: Record<string, number>
  risk_trend: RiskTrendPoint[]
}

export interface EventsResponse {
  items: Event[]
  total: number
  summary: DashboardSummary
}

export interface AnalysisResult {
  event_id: string
  risk_level: string
  risk_score: number
  current_stage: string
  evolution_path: string[]
  risk_signals: RiskSignal[]
  key_comments: string[]
  confidence: number
}

export interface RiskSignal {
  signal_type: string
  score: number
  evidence_text: string
  reason: string
  source: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface GraphNode {
  node_id: string
  label: string
  node_type: string
  size: number
  risk_score: number
}

export interface GraphEdge {
  source: string
  target: string
  edge_type: string
  weight: number
}

export interface Evidence {
  evidence_id: string
  title: string
  source: string
  content: string
  score: number
  evidence_type: string
}

export interface KeyCommentExplanation {
  comment_id: string
  reason: string
  risk_signal: string
}

export interface InterventionAdvice {
  summary: string
  official_statement: string
  action_items: string[]
  avoid_phrases: string[]
  responsible_department: string[]
  urgency: string
}

export interface Report {
  event_id: string
  event_summary: string
  risk_assessment: Pick<AnalysisResult, 'risk_level' | 'risk_score' | 'current_stage' | 'evolution_path' | 'confidence'>
  key_findings: {
    key_comments: string[]
    risk_signals: RiskSignal[]
  }
  key_comment_explanations: KeyCommentExplanation[]
  evidence: Evidence[]
  intervention: InterventionAdvice
  human_review_required: boolean
  generated_at: string
  mode: string
}

export interface SystemConfig {
  llm_provider: string
  llm_endpoint: string
  llm_model: string
  use_llm: boolean
  comment_topn: number
}

export const api = {
  getConfig: () =>
    client.get<SystemConfig>('/config/'),

  updateConfig: (config: Partial<SystemConfig>) =>
    client.put<SystemConfig>('/config/', config),

  checkHealth: () =>
    client.get<{ status: string }>('/health/'),
  getEvents: (params?: { risk_level?: string; event_type?: string }) =>
    client.get<EventsResponse>('/events/', { params }),

  analyzeEvent: (eventId: string) => {
    const useLLM = localStorage.getItem('use_llm') === 'true'
    return client.post<AnalysisResult>(`/analyze/${eventId}`, {
      mode: useLLM ? 'llm' : 'cached',
      use_llm: useLLM,
      llm_provider: localStorage.getItem('llm_provider') || 'openai',
      llm_model: localStorage.getItem('llm_model') || 'gpt-4o',
      comment_topn: Number(localStorage.getItem('comment_topn') || '20'),
      resonance_weights: {
        alpha: Number(localStorage.getItem('resonance_alpha') || '0.30'),
        beta: Number(localStorage.getItem('resonance_beta') || '0.25'),
        gamma: Number(localStorage.getItem('resonance_gamma') || '0.25'),
        delta: Number(localStorage.getItem('resonance_delta') || '0.20'),
      },
      high_risk_threshold: Number(localStorage.getItem('high_risk_threshold') || '65'),
      severe_risk_threshold: Number(localStorage.getItem('severe_risk_threshold') || '85'),
    })
  },

  getGraph: (eventId: string) =>
    client.get<GraphData>(`/graph/${eventId}`),

  getReport: (eventId: string) =>
    client.get<Report>(`/report/${eventId}`),

  exportReport: (eventId: string, format: string = 'md') =>
    client.get(`/report/${eventId}/export`, { params: { format } }),

  compareBaseline: (eventId: string, method: string = 'all') =>
    client.post(`/baseline/${eventId}`, null, { params: { method } })
}
