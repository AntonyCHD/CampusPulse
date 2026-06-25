<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Setting, Cpu, DataAnalysis, Delete, CircleCheck, CircleClose, Refresh, Connection, Promotion, ChatDotRound } from '@element-plus/icons-vue'
import { getLLMConfig, testLLMConnection, chatCompletion, streamChatCompletion, type LLMTestResult } from '../api/llmService'

const activeTab = ref('llm')

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

const playgroundPrompt = ref('你是一个校园舆情分析师。请用一句话介绍你的分析能力。')
const playgroundResponse = ref('')
const playgroundStreaming = ref(false)
const playgroundLoading = ref(false)
const playgroundUsage = ref<{ prompt_tokens: number; completion_tokens: number; total_tokens: number } | null>(null)
const playgroundLatency = ref(0)

const cacheStats = reactive({ llmResponses: 0, demoReports: 0, graphJson: 0, embeddings: 0 })
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
  playgroundLoading.value = true; playgroundResponse.value = ''; playgroundUsage.value = null
  const start = performance.now()
  try {
    if (playgroundStreaming.value) {
      const stream = streamChatCompletion([{ role: 'user', content: playgroundPrompt.value }])
      for await (const chunk of stream) { playgroundResponse.value += chunk; await nextTick() }
    } else {
      const resp = await chatCompletion([{ role: 'user', content: playgroundPrompt.value }])
      playgroundResponse.value = resp.choices?.[0]?.message?.content || '(empty)'
      playgroundUsage.value = resp.usage || null
    }
    playgroundLatency.value = Math.round(performance.now() - start)
  } catch (err: any) {
    playgroundResponse.value = 'Error: ' + (err.message || String(err))
  } finally { playgroundLoading.value = false }
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
  if (confirm('确认清除 ' + cacheType + ' 缓存？')) {
    alert(cacheType + ' 缓存已清除（需后端API支持）')
  }
}

const checkBackendStatus = async () => {
  backendStatus.value = 'checking'
  try { const resp = await fetch('/api/events/'); backendStatus.value = resp.ok ? 'online' : 'offline' }
  catch { backendStatus.value = 'offline' }
}

const providers = [
  { value: 'openai', label: 'OpenAI', defaultEndpoint: 'https://api.openai.com/v1', defaultModel: 'gpt-4o' },
  { value: 'deepseek', label: 'DeepSeek', defaultEndpoint: 'https://api.deepseek.com/v1', defaultModel: 'deepseek-chat' },
  { value: 'qwen', label: '通义千问', defaultEndpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1', defaultModel: 'qwen-plus' },
  { value: 'zhipu', label: '智谱AI', defaultEndpoint: 'https://open.bigmodel.cn/api/paas/v4', defaultModel: 'glm-4' },
  { value: 'custom', label: '自定义', defaultEndpoint: '', defaultModel: '' },
]

const onProviderChange = (val: string) => {
  const p = providers.find(x => x.value === val)
  if (p && p.defaultEndpoint) llmConfig.endpoint = p.defaultEndpoint
  if (p && p.defaultModel) llmConfig.model = p.defaultModel
  saveLLMConfig()
}

const signalTypes = [
  { key: 'negative_emotion', label: '负面情绪', desc: '明显负面情绪表达' },
  { key: 'collective_resonance', label: '集体共鸣', desc: '多人表达相同不满' },
  { key: 'rumor_spread', label: '传闻扩散', desc: '未证实传闻传播' },
  { key: 'sarcasm', label: '反讽暗喻', desc: '谐音梗、阴阳怪气、暗语' },
  { key: 'mobilization', label: '行动号召', desc: '组织化行动表达' },
  { key: 'confrontation', label: '对抗倾向', desc: '立场对立与冲突' },
  { key: 'privacy_leak', label: '隐私泄露', desc: '曝光个人信息' },
  { key: 'offline_risk', label: '线下风险', desc: '时间地点+行动目标' },
]

const tabs = [
  { key: 'llm', label: 'LLM 配置', icon: Cpu },
  { key: 'playground', label: 'Playground', icon: Promotion },
  { key: 'analysis', label: '分析参数', icon: DataAnalysis },
  { key: 'cache', label: '缓存管理', icon: Delete },
  { key: 'system', label: '系统状态', icon: Setting },
]

onMounted(() => { checkBackendStatus() })
</script>

<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>系统配置</h1>
      <p class="subtitle">配置 LLM API、分析参数、数据源与缓存管理</p>
    </div>

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
          <span v-if="llmConnected && llmTestResult">
            已连接: {{ llmTestResult.model }} ({{ llmTestResult.latencyMs }}ms, {{ llmTestResult.usage?.total_tokens || 0 }} tokens)
          </span>
          <span v-else>LLM API 未连接 — 当前使用规则兜底+缓存模式</span>
        </div>
        <el-button size="small" :loading="llmTesting" @click="doTestConnection">
          <Connection style="margin-right:4px" /> 测试连接
        </el-button>
      </div>

      <div v-if="llmTestResult && !llmTestResult.success" class="error-card">
        <div class="error-title">连接失败</div>
        <div class="error-body">{{ llmTestResult.error }}</div>
        <div class="error-hint">检查: endpoint URL、API Key 有效性、网络访问、CORS 策略</div>
      </div>

      <div class="config-grid">
        <div class="config-card">
          <div class="config-card-header">服务商</div>
          <div class="config-card-body">
            <div class="form-group">
              <label>LLM 服务商</label>
              <el-select v-model="llmConfig.provider" @change="onProviderChange" style="width:100%">
                <el-option v-for="p in providers" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
              <span class="form-hint">支持 OpenAI-compatible API 的服务商均可接入</span>
            </div>
            <div class="form-group">
              <label>API Endpoint</label>
              <el-input v-model="llmConfig.endpoint" @change="saveLLMConfig" placeholder="https://api.openai.com/v1" />
              <span class="form-hint">Chat Completions 端点基础 URL</span>
            </div>
            <div class="form-group">
              <label>API Key</label>
              <el-input v-model="llmConfig.apiKey" @change="saveLLMConfig" type="password" placeholder="sk-..." show-password />
              <span class="form-hint">密钥仅存储在浏览器本地，不会上传到服务器</span>
            </div>
          </div>
        </div>

        <div class="config-card">
          <div class="config-card-header">模型参数</div>
          <div class="config-card-body">
            <div class="form-group">
              <label>模型名称</label>
              <el-input v-model="llmConfig.model" @change="saveLLMConfig" placeholder="gpt-4o" />
            </div>
            <div class="form-group">
              <label>Temperature: {{ llmConfig.temperature }}</label>
              <el-slider v-model="llmConfig.temperature" :min="0" :max="1" :step="0.05" @change="saveLLMConfig" />
              <span class="form-hint">越低越确定，越高越随机。结构化研判建议 0.1-0.3</span>
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
          <span>{{ llmConnected ? 'LLM Playground — 直接测试已配置模型' : '请先在"LLM 配置"中配置并测试连接' }}</span>
        </div>
      </div>

      <div class="config-grid">
        <div class="config-card config-card-wide">
          <div class="config-card-header">测试提示词</div>
          <div class="config-card-body">
            <div class="form-group">
              <el-input v-model="playgroundPrompt" type="textarea" :rows="4" placeholder="输入测试提示词..." />
            </div>
            <div style="display:flex;align-items:center;gap:12px;margin-top:12px">
              <el-button type="primary" :loading="playgroundLoading" @click="runPlayground" :disabled="!llmConnected">
                <Promotion style="margin-right:6px" /> 发送
              </el-button>
              <el-checkbox v-model="playgroundStreaming" label="流式输出" size="small" />
              <span v-if="playgroundLatency > 0" class="latency-badge">{{ playgroundLatency }}ms</span>
              <span v-if="playgroundUsage" class="latency-badge">{{ playgroundUsage.total_tokens }} tokens</span>
            </div>
          </div>
        </div>

        <div class="config-card config-card-wide" v-if="playgroundResponse">
          <div class="config-card-header">响应</div>
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
          <span>{{ analysisParams.useLLM ? '已启用 LLM 增强分析 — 语义理解 + 规则兜底' : '仅使用规则兜底模式 — 建议启用 LLM 以检测谐音、反讽、暗喻' }}</span>
        </div>
        <el-switch v-model="analysisParams.useLLM" @change="saveAnalysisParams" active-text="LLM" inactive-text="规则" />
      </div>

      <div class="config-grid">
        <div class="config-card">
          <div class="config-card-header">评论筛选</div>
          <div class="config-card-body">
            <div class="form-group">
              <label>Top-N 评论预过滤: {{ analysisParams.commentTopN }}</label>
              <el-slider v-model="analysisParams.commentTopN" :min="5" :max="50" @change="saveAnalysisParams" />
              <span class="form-hint">按互动强度+语义代表性+风险信号筛选 Top-N 评论送入 LLM</span>
            </div>
            <div class="form-group">
              <label>语义相似度阈值: {{ analysisParams.semanticThreshold }}</label>
              <el-slider v-model="analysisParams.semanticThreshold" :min="0.5" :max="0.95" :step="0.01" @change="saveAnalysisParams" />
              <span class="form-hint">话题聚类的事件归并阈值</span>
            </div>
          </div>
        </div>

        <div class="config-card">
          <div class="config-card-header">情绪共振权重</div>
          <div class="config-card-body">
            <div class="form-group"><label>alpha (负面比例): {{ analysisParams.resonanceAlpha }}</label><el-slider v-model="analysisParams.resonanceAlpha" :min="0.1" :max="0.5" :step="0.05" @change="saveAnalysisParams" /></div>
            <div class="form-group"><label>beta (语义集中度): {{ analysisParams.resonanceBeta }}</label><el-slider v-model="analysisParams.resonanceBeta" :min="0.1" :max="0.5" :step="0.05" @change="saveAnalysisParams" /></div>
            <div class="form-group"><label>gamma (互动放大): {{ analysisParams.resonanceGamma }}</label><el-slider v-model="analysisParams.resonanceGamma" :min="0.1" :max="0.5" :step="0.05" @change="saveAnalysisParams" /></div>
            <div class="form-group"><label>delta (时间密度): {{ analysisParams.resonanceDelta }}</label><el-slider v-model="analysisParams.resonanceDelta" :min="0.1" :max="0.5" :step="0.05" @change="saveAnalysisParams" /></div>
          </div>
        </div>

        <div class="config-card">
          <div class="config-card-header">风险等级阈值</div>
          <div class="config-card-body">
            <div class="form-group"><label>高风险阈值: {{ analysisParams.highRiskThreshold }}</label><el-slider v-model="analysisParams.highRiskThreshold" :min="40" :max="85" @change="saveAnalysisParams" /></div>
            <div class="form-group"><label>严重风险阈值: {{ analysisParams.severeRiskThreshold }}</label><el-slider v-model="analysisParams.severeRiskThreshold" :min="65" :max="100" @change="saveAnalysisParams" /></div>
            <div class="threshold-preview">
              <span class="tp-label">预览:</span>
              <span class="tp-badge" style="background:#ecfdf5;color:#10b981;border-color:#a7f3d0">0-{{ analysisParams.highRiskThreshold - 1 }} 低</span>
              <span class="tp-badge" style="background:#fffbeb;color:#f59e0b;border-color:#fde68a">{{ analysisParams.highRiskThreshold }}-{{ analysisParams.severeRiskThreshold - 1 }} 高</span>
              <span class="tp-badge" style="background:#fef2f2;color:#ef4444;border-color:#fca5a5">{{ analysisParams.severeRiskThreshold }}-100 严重</span>
            </div>
          </div>
        </div>

        <div class="config-card config-card-wide">
          <div class="config-card-header">风险信号类型（8 类）</div>
          <div class="config-card-body">
            <div class="signal-grid">
              <div v-for="s in signalTypes" :key="s.key" class="signal-item">
                <span class="signal-item-label">{{ s.label }}</span>
                <span class="signal-item-desc">{{ s.desc }}</span>
              </div>
            </div>
            <span class="form-hint" style="margin-top:12px;display:block">
              当前使用"语义向量 + 规则兜底 + Top-N LLM 弱标注"策略。启用 LLM 后可检测谐音、反讽、暗喻等隐蔽信号。
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cache Tab -->
    <div v-if="activeTab === 'cache'" class="tab-content">
      <div class="config-grid">
        <div class="config-card config-card-wide">
          <div class="config-card-header">缓存状态</div>
          <div class="config-card-body">
            <div class="cache-grid">
              <div class="cache-item"><span class="cache-num">{{ cacheStats.llmResponses }}</span><span class="cache-label">LLM 响应</span><span class="cache-path">cache/llm_responses/</span></div>
              <div class="cache-item"><span class="cache-num">{{ cacheStats.demoReports }}</span><span class="cache-label">演示报告</span><span class="cache-path">cache/demo_reports/</span></div>
              <div class="cache-item"><span class="cache-num">{{ cacheStats.graphJson }}</span><span class="cache-label">图谱 JSON</span><span class="cache-path">cache/graph_json/</span></div>
              <div class="cache-item"><span class="cache-num">{{ cacheStats.embeddings }}</span><span class="cache-label">向量缓存</span><span class="cache-path">cache/embeddings/</span></div>
            </div>
          </div>
        </div>
        <div class="config-card">
          <div class="config-card-header">缓存操作</div>
          <div class="config-card-body">
            <el-button type="danger" plain @click="clearCache('LLM响应')" style="width:100%;margin-bottom:8px"><Delete style="margin-right:6px" /> 清除 LLM 响应</el-button>
            <el-button type="warning" plain @click="clearCache('演示报告')" style="width:100%;margin-bottom:8px"><Delete style="margin-right:6px" /> 清除演示报告</el-button>
            <el-button type="info" plain @click="clearCache('全部')" style="width:100%"><Delete style="margin-right:6px" /> 清除全部缓存</el-button>
          </div>
        </div>
        <div class="config-card">
          <div class="config-card-header">缓存说明</div>
          <div class="config-card-body">
            <div class="info-text">
              <p>演示模式优先走缓存，避免 LLM API 不稳定影响展示效果。</p>
              <p style="margin-top:8px">Embedding 结果缓存后避免每次重复计算。</p>
              <p style="margin-top:8px">所有大模型输出缓存在 <code>cache/llm_responses/</code>。</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Tab -->
    <div v-if="activeTab === 'system'" class="tab-content">
      <div class="config-grid">
        <div class="config-card">
          <div class="config-card-header">后端状态</div>
          <div class="config-card-body">
            <div class="status-row">
              <span class="status-label">API 服务</span>
              <span v-if="backendStatus === 'checking'" class="status-val checking">检测中...</span>
              <span v-else-if="backendStatus === 'online'" class="status-val online"><CircleCheck style="width:16px;height:16px;vertical-align:-3px" /> 在线</span>
              <span v-else class="status-val offline"><CircleClose style="width:16px;height:16px;vertical-align:-3px" /> 离线</span>
            </div>
            <el-button size="small" @click="checkBackendStatus" :loading="backendStatus === 'checking'" style="margin-top:12px"><Refresh style="margin-right:4px" /> 刷新</el-button>
          </div>
        </div>
        <div class="config-card">
          <div class="config-card-header">LLM 状态</div>
          <div class="config-card-body">
            <div class="status-row">
              <span class="status-label">服务商</span>
              <span class="status-val mono">{{ llmConfig.provider }} / {{ llmConfig.model }}</span>
            </div>
            <div class="status-row" style="margin-top:8px">
              <span class="status-label">连接</span>
              <span v-if="llmConnected" class="status-val online">已连接</span>
              <span v-else class="status-val offline">未连接</span>
            </div>
            <div class="status-row" style="margin-top:8px" v-if="llmTestResult">
              <span class="status-label">延迟</span>
              <span class="status-val mono">{{ llmTestResult.latencyMs }}ms</span>
            </div>
          </div>
        </div>
        <div class="config-card config-card-wide">
          <div class="config-card-header">技术栈</div>
          <div class="config-card-body">
            <div class="tech-stack">
              <div class="tech-item"><span class="tech-label">前端</span><span class="tech-val">Vue 3 + TypeScript + Element Plus + ECharts + vis-network</span></div>
              <div class="tech-item"><span class="tech-label">后端</span><span class="tech-val">FastAPI + Pydantic</span></div>
              <div class="tech-item"><span class="tech-label">存储</span><span class="tech-val">SQLite / DuckDB + FAISS / Chroma</span></div>
              <div class="tech-item"><span class="tech-label">语义</span><span class="tech-val">BGE-M3 / bge-large-zh-v1.5 / gte-Qwen2</span></div>
              <div class="tech-item"><span class="tech-label">图谱</span><span class="tech-val">NetworkX</span></div>
              <div class="tech-item"><span class="tech-label">LLM</span><span class="tech-val">OpenAI-compatible SDK ({{ llmConfig.provider }} / {{ llmConfig.model }})</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page { max-width:1200px; margin:0 auto; padding:20px 24px; }
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
.tech-label { font-weight:600; color:#1E3A8A; min-width:48px; }
.tech-val { color:#64748B; }
</style>