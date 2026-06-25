import os

views = r"C:\Users\31982\Desktop\代码\舆情与媒体安全\frontend-vue\src\views"

settings = """<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Setting, Cpu, DataAnalysis, Delete, CircleCheck, CircleClose, Refresh, Connection, ChatDotRound, Promotion } from '@element-plus/icons-vue'
import { getLLMConfig, testLLMConnection, chatCompletion, streamChatCompletion, type LLMTestResult } from '../api/llmService'

const activeTab = ref('llm')

// LLM Config
const llmConfig = reactive({
  provider: localStorage.getItem('llm_provider') || 'openai',
  endpoint: localStorage.getItem('llm_endpoint') || 'https://api.openai.com/v1',
  apiKey: localStorage.getItem('llm_api_key') || '',
  model: localStorage.getItem('llm_model') || 'gpt-4o',
  temperature: Number(localStorage.getItem('llm_temperature') || '0.3'),
  maxTokens: Number(localStorage.getItem('llm_max_tokens') || '2048'),
})

const llmConnected = ref(false)
const llmTestResult = ref<LLMTestResult | null>(null)
const llmTesting = ref(false)

// Analysis Params
const analysisParams = reactive({
  useLLM: localStorage.getItem('use_llm') === 'true',
  commentTopN: Number(localStorage.getItem('comment_topn') || '20'),
  resonanceAlpha: Number(localStorage.getItem('resonance_alpha') || '0.30'),
  resonanceBeta: Number(localStorage.getItem('resonance_beta') || '0.25'),
  resonanceGamma: Number(localStorage.getItem('resonance_gamma') || '0.25'),
  resonanceDelta: Number(localStorage.getItem('resonance_delta') || '0.20'),
  highRiskThreshold: Number(localStorage.getItem('high_risk_threshold') || '65'),
  severeRiskThreshold: Number(localStorage.getItem('severe_risk_threshold') || '85'),
  semanticThreshold: Number(localStorage.getItem('semantic_threshold') || '0.78'),
})

// Playground
const playgroundPrompt = ref('你是一个校园舆情分析师。请用一句话介绍你的分析能力。')
const playgroundResponse = ref('')
const playgroundStreaming = ref(false)
const playgroundLoading = ref(false)
const playgroundUsage = ref<{ prompt_tokens: number; completion_tokens: number; total_tokens: number } | null>(null)
const playgroundLatency = ref(0)

// Cache
const cacheStats = reactive({ llmResponses: 0, demoReports: 0, graphJson: 0, embeddings: 0 })

// System
const backendStatus = ref<'checking' | 'online' | 'offline'>('checking')

const saveLLMConfig = () => {
  for (const [key, val] of Object.entries(llmConfig)) {
    localStorage.setItem('llm_' + key, String(val))
  }
}

const doTestConnection = async () => {
  llmTesting.value = true
  saveLLMConfig()
  llmTestResult.value = await testLLMConnection()
  llmConnected.value = llmTestResult.value.success
  llmTesting.value = false
}

const runPlayground = async () => {
  if (!playgroundPrompt.value.trim()) return
  playgroundLoading.value = true
  playgroundResponse.value = ''
  playgroundUsage.value = null
  const start = performance.now()

  try {
    if (playgroundStreaming.value) {
      const stream = streamChatCompletion([{ role: 'user', content: playgroundPrompt.value }])
      for await (const chunk of stream) {
        playgroundResponse.value += chunk
        await nextTick()
      }
    } else {
      const resp = await chatCompletion([{ role: 'user', content: playgroundPrompt.value }])
      playgroundResponse.value = resp.choices?.[0]?.message?.content || '(empty response)'
      playgroundUsage.value = resp.usage || null
    }
    playgroundLatency.value = Math.round(performance.now() - start)
  } catch (err: any) {
    playgroundResponse.value = 'Error: ' + (err.message || String(err))
  } finally {
    playgroundLoading.value = false
  }
}

const saveAnalysisParams = () => {
  const keys: Record<string, string> = {
    useLLM: 'use_llm', commentTopN: 'comment_topn',
    resonanceAlpha: 'resonance_alpha', resonanceBeta: 'resonance_beta',
    resonanceGamma: 'resonance_gamma', resonanceDelta: 'resonance_delta',
    highRiskThreshold: 'high_risk_threshold', severeRiskThreshold: 'severe_risk_threshold',
    semanticThreshold: 'semantic_threshold',
  }
  for (const [k, v] of Object.entries(analysisParams)) {
    localStorage.setItem(keys[k] || k, String(v))
  }
}

const clearCache = (cacheType: string) => {
  if (confirm('Confirm clear: ' + cacheType + ' cache?')) {
    alert(cacheType + ' cache cleared (needs backend API support)')
  }
}

const checkBackendStatus = async () => {
  backendStatus.value = 'checking'
  try {
    const resp = await fetch('/api/events/')
    backendStatus.value = resp.ok ? 'online' : 'offline'
  } catch {
    backendStatus.value = 'offline'
  }
}

const providers = [
  { value: 'openai', label: 'OpenAI', defaultEndpoint: 'https://api.openai.com/v1', defaultModel: 'gpt-4o' },
  { value: 'deepseek', label: 'DeepSeek', defaultEndpoint: 'https://api.deepseek.com/v1', defaultModel: 'deepseek-chat' },
  { value: 'qwen', label: 'Qwen (通义千问)', defaultEndpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1', defaultModel: 'qwen-plus' },
  { value: 'zhipu', label: 'Zhipu (智谱AI)', defaultEndpoint: 'https://open.bigmodel.cn/api/paas/v4', defaultModel: 'glm-4' },
  { value: 'custom', label: 'Custom', defaultEndpoint: '', defaultModel: '' },
]

const onProviderChange = (val: string) => {
  const p = providers.find(x => x.value === val)
  if (p && p.defaultEndpoint) llmConfig.endpoint = p.defaultEndpoint
  if (p && p.defaultModel) llmConfig.model = p.defaultModel
  saveLLMConfig()
}

const signalTypes = [
  { key: 'negative_emotion', label: 'Negative Emotion', desc: 'Obvious negative sentiment' },
  { key: 'collective_resonance', label: 'Collective Resonance', desc: 'Multiple users express same complaint' },
  { key: 'rumor_spread', label: 'Rumor Spread', desc: 'Unverified claims circulating' },
  { key: 'sarcasm', label: 'Sarcasm / Innuendo', desc: 'Homophonic puns, irony, coded language' },
  { key: 'mobilization', label: 'Mobilization', desc: 'Calls for collective action' },
  { key: 'confrontation', label: 'Confrontation', desc: 'Polarization and conflict' },
  { key: 'privacy_leak', label: 'Privacy Leak', desc: 'Exposure of personal information' },
  { key: 'offline_risk', label: 'Offline Risk', desc: 'Time + location + action target' },
]

const tabs = [
  { key: 'llm', label: 'LLM Config', icon: Cpu },
  { key: 'playground', label: 'Playground', icon: Promotion },
  { key: 'analysis', label: 'Analysis Params', icon: DataAnalysis },
  { key: 'cache', label: 'Cache', icon: Delete },
  { key: 'system', label: 'System', icon: Setting },
]

onMounted(() => { checkBackendStatus() })
</script>

<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>System Configuration</h1>
      <p class="subtitle">LLM API, analysis parameters, data sources & cache management</p>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button v-for="tab in tabs" :key="tab.key" class="tab-btn" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
        <component :is="tab.icon" class="tab-icon" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- LLM Config Tab -->
    <div v-if="activeTab === 'llm'" class="tab-content">
      <div class="status-banner" :class="llmConnected ? 'banner-ok' : 'banner-warn'">
        <div class="banner-left">
          <CircleCheck v-if="llmConnected" class="banner-icon" style="color:#10b981" />
          <CircleClose v-else class="banner-icon" style="color:#f59e0b" />
          <span v-if="llmConnected && llmTestResult">Connected: {{ llmTestResult.model }} ({{ llmTestResult.latencyMs }}ms, {{ llmTestResult.usage?.total_tokens || 0 }} tokens)</span>
          <span v-else>LLM API not connected &mdash; using rule-based fallback + cache mode</span>
        </div>
        <el-button size="small" :loading="llmTesting" @click="doTestConnection">
          <Connection style="margin-right:4px" /> Test Connection
        </el-button>
      </div>

      <!-- Test Result Detail -->
      <div v-if="llmTestResult && !llmTestResult.success" class="error-card">
        <div class="error-title">Connection Failed</div>
        <div class="error-body">{{ llmTestResult.error }}</div>
        <div class="error-hint">Check: endpoint URL, API key validity, network access, CORS policy</div>
      </div>

      <div class="config-grid">
        <div class="config-card">
          <div class="config-card-header">Provider</div>
          <div class="config-card-body">
            <div class="form-group">
              <label>LLM Provider</label>
              <el-select v-model="llmConfig.provider" @change="onProviderChange" style="width:100%">
                <el-option v-for="p in providers" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
              <span class="form-hint">Any OpenAI-compatible API provider works</span>
            </div>
            <div class="form-group">
              <label>API Endpoint</label>
              <el-input v-model="llmConfig.endpoint" @change="saveLLMConfig" placeholder="https://api.openai.com/v1" />
              <span class="form-hint">Chat completions endpoint base URL</span>
            </div>
            <div class="form-group">
              <label>API Key</label>
              <el-input v-model="llmConfig.apiKey" @change="saveLLMConfig" type="password" placeholder="sk-..." show-password />
              <span class="form-hint">Key stored in browser localStorage only, never sent to our server</span>
            </div>
          </div>
        </div>

        <div class="config-card">
          <div class="config-card-header">Model Parameters</div>
          <div class="config-card-body">
            <div class="form-group">
              <label>Model Name</label>
              <el-input v-model="llmConfig.model" @change="saveLLMConfig" placeholder="gpt-4o" />
            </div>
            <div class="form-group">
              <label>Temperature: {{ llmConfig.temperature }}</label>
              <el-slider v-model="llmConfig.temperature" :min="0" :max="1" :step="0.05" @change="saveLLMConfig" />
              <span class="form-hint">Lower = more deterministic. For structured analysis: 0.1&ndash;0.3</span>
            </div>
            <div class="form-group">
              <label>Max Tokens: {{ llmConfig.maxTokens }}</label>
              <el-slider v-model="llmConfig.maxTokens" :min="512" :max="8192" :step="256" @change="saveLLMConfig" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Playground Tab -->
    <div v-if="activeTab === 'playground'" class="tab-content">
      <div class="status-banner" :class="llmConnected ? 'banner-ok' : 'banner-warn'">
        <div class="banner-left">
          <Promotion class="banner-icon" :style="{ color: llmConnected ? '#10b981' : '#f59e0b' }" />
          <span>{{ llmConnected ? 'LLM Playground &mdash; test prompts directly against the configured model' : 'Configure and test LLM connection first in the LLM Config tab' }}</span>
        </div>
      </div>

      <div class="config-grid">
        <div class="config-card config-card-wide">
          <div class="config-card-header">Test Prompt</div>
          <div class="config-card-body">
            <div class="form-group">
              <el-input
                v-model="playgroundPrompt"
                type="textarea"
                :rows="4"
                placeholder="Enter your test prompt..."
              />
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-top:12px">
              <el-button type="primary" :loading="playgroundLoading" @click="runPlayground" :disabled="!llmConnected">
                <Promotion style="margin-right:6px" /> Send
              </el-button>
              <el-checkbox v-model="playgroundStreaming" label="Stream output" size="small" />
              <span v-if="playgroundLatency > 0" class="latency-badge">{{ playgroundLatency }}ms</span>
              <span v-if="playgroundUsage" class="latency-badge">{{ playgroundUsage.total_tokens }} tokens</span>
            </div>
          </div>
        </div>

        <div class="config-card config-card-wide" v-if="playgroundResponse">
          <div class="config-card-header">Response</div>
          <div class="config-card-body">
            <div class="response-box" :class="{ streaming: playgroundStreaming && playgroundLoading }">{{ playgroundResponse }}</div>
            <div v-if="playgroundUsage" class="usage-detail">
              <span>Prompt: {{ playgroundUsage.prompt_tokens }}</span>
              <span>Completion: {{ playgroundUsage.completion_tokens }}</span>
              <span>Total: {{ playgroundUsage.total_tokens }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Analysis Params Tab -->
    <div v-if="activeTab === 'analysis'" class="tab-content">
      <div class="status-banner" :class="analysisParams.useLLM ? 'banner-ok' : 'banner-warn'">
        <div class="banner-left">
          <Cpu class="banner-icon" :style="{ color: analysisParams.useLLM ? '#10b981' : '#f59e0b' }" />
          <span>{{ analysisParams.useLLM ? 'LLM-enhanced analysis enabled &mdash; semantic understanding + rule fallback' : 'Rule-only fallback mode &mdash; enable LLM for sarcasm, homophonic puns, metaphor detection' }}</span>
        </div>
        <el-switch v-model="analysisParams.useLLM" @change="saveAnalysisParams" active-text="LLM" inactive-text="Rules" />
      </div>

      <div class="config-grid">
        <div class="config-card">
          <div class="config-card-header">Comment Filtering</div>
          <div class="config-card-body">
            <div class="form-group">
              <label>Top-N Comment Preselection: {{ analysisParams.commentTopN }}</label>
              <el-slider v-model="analysisParams.commentTopN" :min="5" :max="50" @change="saveAnalysisParams" />
              <span class="form-hint">Filter by interaction + semantic representativeness + risk signals before sending to LLM</span>
            </div>
            <div class="form-group">
              <label>Semantic Similarity Threshold: {{ analysisParams.semanticThreshold }}</label>
              <el-slider v-model="analysisParams.semanticThreshold" :min="0.5" :max="0.95" :step="0.01" @change="saveAnalysisParams" />
              <span class="form-hint">Event clustering merge threshold</span>
            </div>
          </div>
        </div>

        <div class="config-card">
          <div class="config-card-header">Resonance Score Weights</div>
          <div class="config-card-body">
            <div class="form-group"><label>alpha (negative ratio): {{ analysisParams.resonanceAlpha }}</label><el-slider v-model="analysisParams.resonanceAlpha" :min="0.1" :max="0.5" :step="0.05" @change="saveAnalysisParams" /></div>
            <div class="form-group"><label>beta (semantic concentration): {{ analysisParams.resonanceBeta }}</label><el-slider v-model="analysisParams.resonanceBeta" :min="0.1" :max="0.5" :step="0.05" @change="saveAnalysisParams" /></div>
            <div class="form-group"><label>gamma (interaction amplification): {{ analysisParams.resonanceGamma }}</label><el-slider v-model="analysisParams.resonanceGamma" :min="0.1" :max="0.5" :step="0.05" @change="saveAnalysisParams" /></div>
            <div class="form-group"><label>delta (temporal density): {{ analysisParams.resonanceDelta }}</label><el-slider v-model="analysisParams.resonanceDelta" :min="0.1" :max="0.5" :step="0.05" @change="saveAnalysisParams" /></div>
          </div>
        </div>

        <div class="config-card">
          <div class="config-card-header">Risk Thresholds</div>
          <div class="config-card-body">
            <div class="form-group"><label>High Risk: {{ analysisParams.highRiskThreshold }}</label><el-slider v-model="analysisParams.highRiskThreshold" :min="40" :max="85" @change="saveAnalysisParams" /></div>
            <div class="form-group"><label>Severe Risk: {{ analysisParams.severeRiskThreshold }}</label><el-slider v-model="analysisParams.severeRiskThreshold" :min="65" :max="100" @change="saveAnalysisParams" /></div>
            <div class="threshold-preview">
              <span class="tp-label">Preview:</span>
              <span class="tp-badge" style="background:#ecfdf5;color:#10b981;border-color:#a7f3d0">0-{{ analysisParams.highRiskThreshold - 1 }} Low</span>
              <span class="tp-badge" style="background:#fffbeb;color:#f59e0b;border-color:#fde68a">{{ analysisParams.highRiskThreshold }}-{{ analysisParams.severeRiskThreshold - 1 }} High</span>
              <span class="tp-badge" style="background:#fef2f2;color:#ef4444;border-color:#fca5a5">{{ analysisParams.severeRiskThreshold }}-100 Severe</span>
            </div>
          </div>
        </div>

        <div class="config-card config-card-wide">
          <div class="config-card-header">Risk Signal Types (8 categories)</div>
          <div class="config-card-body">
            <div class="signal-grid">
              <div v-for="s in signalTypes" :key="s.key" class="signal-item">
                <span class="signal-item-label">{{ s.label }}</span>
                <span class="signal-item-desc">{{ s.desc }}</span>
              </div>
            </div>
            <span class="form-hint" style="margin-top:12px;display:block">Uses &ldquo;semantic vector + rule fallback + Top-N LLM weak labeling&rdquo; strategy. LLM detects sarcasm, homophonic puns, metaphors, and other covert signals.</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cache Tab -->
    <div v-if="activeTab === 'cache'" class="tab-content">
      <div class="config-grid">
        <div class="config-card config-card-wide">
          <div class="config-card-header">Cache Status</div>
          <div class="config-card-body">
            <div class="cache-grid">
              <div class="cache-item"><span class="cache-num">{{ cacheStats.llmResponses }}</span><span class="cache-label">LLM Responses</span><span class="cache-path">cache/llm_responses/</span></div>
              <div class="cache-item"><span class="cache-num">{{ cacheStats.demoReports }}</span><span class="cache-label">Demo Reports</span><span class="cache-path">cache/demo_reports/</span></div>
              <div class="cache-item"><span class="cache-num">{{ cacheStats.graphJson }}</span><span class="cache-label">Graph JSON</span><span class="cache-path">cache/graph_json/</span></div>
              <div class="cache-item"><span class="cache-num">{{ cacheStats.embeddings }}</span><span class="cache-label">Embeddings</span><span class="cache-path">cache/embeddings/</span></div>
            </div>
          </div>
        </div>
        <div class="config-card">
          <div class="config-card-header">Clear Cache</div>
          <div class="config-card-body">
            <el-button type="danger" plain @click="clearCache('LLM response')" style="width:100%;margin-bottom:8px"><Delete style="margin-right:6px" /> Clear LLM Responses</el-button>
            <el-button type="warning" plain @click="clearCache('Demo report')" style="width:100%;margin-bottom:8px"><Delete style="margin-right:6px" /> Clear Demo Reports</el-button>
            <el-button type="info" plain @click="clearCache('All')" style="width:100%"><Delete style="margin-right:6px" /> Clear All Cache</el-button>
          </div>
        </div>
        <div class="config-card">
          <div class="config-card-header">Cache Policy</div>
          <div class="config-card-body">
            <div class="info-text">
              <p>Demo mode prefers cache to avoid LLM API instability.</p>
              <p style="margin-top:8px">Embedding results cached to avoid recomputation.</p>
              <p style="margin-top:8px">All LLM outputs cached in <code>cache/llm_responses/</code>.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Tab -->
    <div v-if="activeTab === 'system'" class="tab-content">
      <div class="config-grid">
        <div class="config-card">
          <div class="config-card-header">Backend Status</div>
          <div class="config-card-body">
            <div class="status-row">
              <span class="status-label">API Service</span>
              <span v-if="backendStatus === 'checking'" class="status-val checking">Checking...</span>
              <span v-else-if="backendStatus === 'online'" class="status-val online"><CircleCheck style="width:16px;height:16px;vertical-align:-3px" /> Online</span>
              <span v-else class="status-val offline"><CircleClose style="width:16px;height:16px;vertical-align:-3px" /> Offline</span>
            </div>
            <el-button size="small" @click="checkBackendStatus" :loading="backendStatus === 'checking'" style="margin-top:12px"><Refresh style="margin-right:4px" /> Refresh</el-button>
          </div>
        </div>
        <div class="config-card">
          <div class="config-card-header">LLM Status</div>
          <div class="config-card-body">
            <div class="status-row">
              <span class="status-label">Provider</span>
              <span class="status-val mono">{{ llmConfig.provider }} / {{ llmConfig.model }}</span>
            </div>
            <div class="status-row" style="margin-top:8px">
              <span class="status-label">Connection</span>
              <span v-if="llmConnected" class="status-val online">Connected</span>
              <span v-else class="status-val offline">Not connected</span>
            </div>
            <div class="status-row" style="margin-top:8px" v-if="llmTestResult">
              <span class="status-label">Latency</span>
              <span class="status-val mono">{{ llmTestResult.latencyMs }}ms</span>
            </div>
          </div>
        </div>
        <div class="config-card config-card-wide">
          <div class="config-card-header">Tech Stack</div>
          <div class="config-card-body">
            <div class="tech-stack">
              <div class="tech-item"><span class="tech-label">Frontend</span><span class="tech-val">Vue 3 + TypeScript + Element Plus + ECharts + vis-network</span></div>
              <div class="tech-item"><span class="tech-label">Backend</span><span class="tech-val">FastAPI + Pydantic</span></div>
              <div class="tech-item"><span class="tech-label">Storage</span><span class="tech-val">SQLite / DuckDB + FAISS / Chroma</span></div>
              <div class="tech-item"><span class="tech-label">Embedding</span><span class="tech-val">BGE-M3 / bge-large-zh-v1.5 / gte-Qwen2</span></div>
              <div class="tech-item"><span class="tech-label">Graph</span><span class="tech-val">NetworkX</span></div>
              <div class="tech-item"><span class="tech-label">LLM</span><span class="tech-val">OpenAI-compatible SDK ({{ llmConfig.provider }} / {{ llmConfig.model }})</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page { max-width:1200px; margin:0 auto; padding:24px; }
.page-header { margin-bottom:24px; }
.page-header h1 { font-family:var(--font-heading,'Fira Code',monospace); font-size:24px; font-weight:600; color:#1E3A8A; margin:0 0 6px 0; }
.subtitle { font-size:14px; color:#64748B; margin:0; }

.tab-bar { display:flex; gap:4px; margin-bottom:24px; background:white; border:1px solid #DBEAFE; border-radius:10px; padding:4px; overflow-x:auto; }
.tab-btn { display:flex; align-items:center; gap:8px; padding:10px 18px; border:none; border-radius:8px; background:transparent; color:#64748B; font-size:13px; font-family:var(--font-body); cursor:pointer; transition:all 0.15s; white-space:nowrap; }
.tab-btn:hover { background:rgba(30,64,175,0.04); color:#1E40AF; }
.tab-btn.active { background:rgba(30,64,175,0.08); color:#1E40AF; font-weight:600; }
.tab-icon { width:16px; height:16px; }

.tab-content { min-height:400px; }

.status-banner { display:flex; align-items:center; justify-content:space-between; padding:14px 20px; border-radius:10px; margin-bottom:20px; }
.banner-ok { background:#f0fdf4; border:1px solid #bbf7d0; }
.banner-warn { background:#fffbeb; border:1px solid #fde68a; }
.banner-left { display:flex; align-items:center; gap:10px; font-size:14px; color:#475569; flex:1; }
.banner-icon { width:20px; height:20px; flex-shrink:0; }

.error-card { background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:16px 20px; margin-bottom:20px; }
.error-title { font-size:14px; font-weight:600; color:#DC2626; margin-bottom:6px; }
.error-body { font-size:13px; color:#475569; font-family:var(--font-heading); word-break:break-all; margin-bottom:8px; }
.error-hint { font-size:12px; color:#94a3b8; }

.config-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.config-card { background:white; border:1px solid #DBEAFE; border-radius:10px; overflow:hidden; }
.config-card-wide { grid-column:1/-1; }
.config-card-header { font-family:var(--font-heading); font-size:13px; font-weight:600; color:#1E3A8A; padding:14px 20px; border-bottom:1px solid #f1f5f9; }
.config-card-body { padding:16px 20px; }

.form-group { margin-bottom:16px; }
.form-group:last-child { margin-bottom:0; }
.form-group label { display:block; font-size:13px; font-weight:500; color:#475569; margin-bottom:6px; }
.form-hint { display:block; font-size:11px; color:#94a3b8; margin-top:4px; }

.latency-badge { font-family:var(--font-heading); font-size:12px; color:#64748B; background:#f1f5f9; padding:2px 10px; border-radius:10px; }

.response-box { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:16px; font-size:14px; color:#1e293b; line-height:1.7; white-space:pre-wrap; min-height:80px; max-height:400px; overflow-y:auto; }
.response-box.streaming { border-color:#3B82F6; }

.usage-detail { display:flex; gap:16px; margin-top:8px; font-size:11px; color:#94a3b8; font-family:var(--font-heading); }

.threshold-preview { display:flex; align-items:center; gap:8px; margin-top:8px; }
.tp-label { font-size:12px; color:#64748B; }
.tp-badge { font-size:11px; font-weight:600; padding:2px 10px; border-radius:4px; border:1px solid; }

.signal-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; }
.signal-item { padding:10px 12px; background:#f8fafc; border-radius:8px; }
.signal-item-label { display:block; font-size:13px; font-weight:600; color:#1E3A8A; margin-bottom:2px; }
.signal-item-desc { font-size:11px; color:#94a3b8; }

.cache-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
.cache-item { text-align:center; padding:16px 12px; background:#f8fafc; border-radius:8px; }
.cache-num { display:block; font-family:var(--font-heading); font-size:28px; font-weight:700; color:#1E3A8A; }
.cache-label { display:block; font-size:12px; color:#64748B; margin-top:4px; }
.cache-path { display:block; font-size:10px; color:#94a3b8; margin-top:4px; font-family:var(--font-heading); }

.status-row { display:flex; align-items:center; justify-content:space-between; }
.status-label { font-size:13px; color:#64748B; }
.status-val { font-size:14px; font-weight:500; }
.status-val.mono { font-family:var(--font-heading); }
.status-val.online { color:#10b981; }
.status-val.offline { color:#ef4444; }
.status-val.checking { color:#94a3b8; }

.info-text { font-size:13px; color:#64748B; line-height:1.6; }
.info-text code { font-family:var(--font-heading); font-size:12px; background:#f1f5f9; padding:1px 6px; border-radius:3px; color:#1E40AF; }

.tech-stack { display:flex; flex-direction:column; gap:8px; }
.tech-item { display:flex; gap:12px; font-size:13px; }
.tech-label { font-weight:600; color:#1E3A8A; min-width:80px; }
.tech-val { color:#64748B; }
</style>
"""

with open(os.path.join(views, "Settings.vue"), "w", encoding="utf-8") as f:
    f.write(settings)
print("Settings.vue updated OK, size:", len(settings))