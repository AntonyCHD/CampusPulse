<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, type AnalysisResult, type Event } from '../api/client'
import { ArrowLeft, DocumentCopy, Share, Warning, TrendCharts, ChatLineSquare, Clock } from '@element-plus/icons-vue'
import SkeletonPresets from '../components/SkeletonPresets.vue'

const route = useRoute()
const router = useRouter()
const eventId = ref(route.params.id as string)
const result = ref<AnalysisResult | null>(null)
const eventDetail = ref<Event | null>(null)
const loading = ref(false)

const analyze = async () => {
  loading.value = true
  try {
    const [analysisResp, eventsResp] = await Promise.all([
      api.analyzeEvent(eventId.value),
      api.getEvents()
    ])
    result.value = analysisResp.data
    if (result.value && result.value.risk_signals) {
      const signalMap = new Map()
      for (const signal of result.value.risk_signals) {
        const key = (signal as any).comment_id || signal.evidence_text
        if (signalMap.has(key)) {
          const existing = signalMap.get(key)
          existing.signal_type += ', ' + signal.signal_type
          existing.score = Math.max(existing.score, signal.score)
        } else {
          signalMap.set(key, { ...signal })
        }
      }
      result.value.risk_signals = Array.from(signalMap.values())
    }
    eventDetail.value = eventsResp.data.items.find(e => e.event_id === eventId.value) || null
  } catch (error) {
    console.error('Analysis failed:', error)
  } finally {
    loading.value = false
  }
}

const viewGraph = () => { router.push('/graph/' + eventId.value) }
const goToIntervention = () => { router.push('/intervention/' + eventId.value) }
const exportReport = () => { router.push('/report/' + eventId.value) }

const getRiskColor = (level: string) => {
  const colors: Record<string, string> = {
    '低': '#10b981', '中': '#f59e0b', '高': '#f97316', '严重': '#ef4444'
  }
  return colors[level] || '#6b7684'
}

onMounted(() => { analyze() })
</script>

<template>
  <div class="event-analysis">
    <div class="page-header">
      <el-button :icon="ArrowLeft" circle @click="router.back()" class="back-button" />
      <div class="header-title">
        <h1>事件分析</h1>
        <el-tag size="large" type="info">{{ eventId }}</el-tag>
      </div>
      <div class="header-actions">
        <el-button :icon="DocumentCopy" @click="viewGraph" size="large">评论图谱</el-button>
        <el-button :icon="Share" type="primary" @click="exportReport" size="large">导出报告</el-button>
      </div>
    </div>

    <!-- Skeleton Loading -->
    <template v-if="loading">
      <SkeletonPresets section="post-card" />
      <SkeletonPresets section="metrics" />
      <SkeletonPresets section="steps" />
      <SkeletonPresets section="two-col" />
    </template>

    <!-- Real Content -->
    <div v-else class="analysis-content">
      <div class="post-card" v-if="eventDetail">
        <div class="post-header">
          <div class="post-header-left">
            <span class="post-type-tag">{{ eventDetail.event_type }}</span>
            <span class="post-time"><Clock style="width:14px;height:14px;vertical-align:-2px" /> {{ eventDetail.created_at }}</span>
          </div>
          <div class="post-header-right">
            <span class="post-stat">{{ eventDetail.comment_count }} 评论</span>
            <span class="post-stat">{{ eventDetail.like_count }} 点赞</span>
          </div>
        </div>
        <h2 class="post-title">{{ eventDetail.title }}</h2>
        <div class="post-body">该事件当前包含 {{ eventDetail.comment_count }} 条评论，点赞数 {{ eventDetail.like_count }}。系统已对评论区进行语义分析、风险信号识别与演化阶段研判。</div>
      </div>

      <div v-if="result">
        <div class="metrics-grid">
          <div class="metric-card" :style="{ borderLeftColor: getRiskColor(result.risk_level), borderLeftWidth: '3px' }">
            <div class="metric-icon" :style="{ background: getRiskColor(result.risk_level) + '18', color: getRiskColor(result.risk_level) }">
              <Warning style="width:24px;height:24px" />
            </div>
            <div class="metric-content">
              <div class="metric-label">风险等级</div>
              <div class="metric-value" :style="{ color: getRiskColor(result.risk_level) }">{{ result.risk_level }}</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon" style="background:#eff6ff;color:#3b82f6"><span class="metric-num-big">{{ result.risk_score.toFixed(0) }}</span></div>
            <div class="metric-content"><div class="metric-label">风险分数</div><div class="metric-value">{{ result.risk_score.toFixed(2) }}</div></div>
          </div>
          <div class="metric-card">
            <div class="metric-icon" style="background:#f0fdf4;color:#10b981"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></div>
            <div class="metric-content"><div class="metric-label">当前阶段</div><div class="metric-value stage-value">{{ result.current_stage }}</div></div>
          </div>
          <div class="metric-card">
            <div class="metric-icon" style="background:#fef3f2;color:#f97316"><span class="metric-num-big">{{ (result.confidence * 100).toFixed(0) }}%</span></div>
            <div class="metric-content"><div class="metric-label">置信度</div><div class="metric-value">{{ (result.confidence * 100).toFixed(1) }}%</div></div>
          </div>
        </div>

        <div class="section-card">
          <div class="section-header"><TrendCharts class="section-icon-svg" /><span class="section-title">演化路径</span></div>
          <el-steps :active="result.evolution_path.length" align-center class="evolution-steps">
            <el-step v-for="(stage, index) in result.evolution_path" :key="index" :title="stage" />
          </el-steps>
        </div>

        <div class="analysis-grid">
          <div class="section-card">
            <div class="section-header"><Warning class="section-icon-svg" style="color:#f97316" /><span class="section-title">风险信号</span><el-tag type="warning" size="large">{{ result.risk_signals.length }} 个</el-tag></div>
            <el-table :data="result.risk_signals" class="signals-table" :stripe="true" size="small">
              <el-table-column prop="signal_type" label="信号类型" width="140"><template #default="{ row }"><el-tag size="small" effect="dark">{{ row.signal_type }}</el-tag></template></el-table-column>
              <el-table-column prop="score" label="分数" width="80" align="center"><template #default="{ row }"><span class="signal-score">{{ row.score.toFixed(2) }}</span></template></el-table-column>
              <el-table-column prop="evidence_text" label="证据文本" min-width="220" show-overflow-tooltip />
              <el-table-column prop="reason" label="识别原因" min-width="180" show-overflow-tooltip />
              <el-table-column prop="source" label="来源" width="80" align="center"><template #default="{ row }"><el-tag type="info" size="small" effect="plain">{{ row.source }}</el-tag></template></el-table-column>
            </el-table>
          </div>
          <div class="section-card">
            <div class="section-header"><ChatLineSquare class="section-icon-svg" style="color:#10b981" /><span class="section-title">关键评论</span><el-tag type="success" size="large">{{ result.key_comments.length }} 个</el-tag></div>
            <div v-if="result.key_comments.length > 0" class="comments-grid">
              <div v-for="(cid, index) in result.key_comments" :key="index" class="key-comment-item"><span class="kc-index">{{ index + 1 }}</span><span class="kc-id">{{ cid }}</span></div>
            </div>
            <el-empty v-else description="未识别到关键评论" :image-size="80" />
          </div>
        </div>

        <div class="action-row">
          <el-button type="primary" size="large" @click="viewGraph"><DocumentCopy style="margin-right:6px" /> 查看评论链图谱</el-button>
          <el-button size="large" @click="goToIntervention">查看处置方案</el-button>
          <el-button size="large" @click="exportReport">导出分析报告</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.event-analysis { padding: 16px 24px; }
.page-header { margin-bottom:24px; display:flex; align-items:center; gap:20px; }
.back-button { flex-shrink:0; }
.header-title { flex:1; display:flex; align-items:center; gap:16px; }
.header-title h1 { font-family:var(--font-heading,'Fira Code',monospace); font-size:24px; font-weight:600; color:#1E3A8A; margin:0; }
.header-actions { display:flex; gap:12px; }
.post-card { background:white; border:1px solid #DBEAFE; border-radius:10px; padding: 16px 24px; margin-bottom:20px; }
.post-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.post-header-left,.post-header-right { display:flex; align-items:center; gap:12px; }
.post-type-tag { font-size:12px; font-weight:600; padding:2px 10px; border-radius:4px; background:rgba(30,64,175,0.08); color:#1E40AF; }
.post-time { font-size:12px; color:#94a3b8; display:flex; align-items:center; gap:4px; }
.post-stat { font-size:12px; color:#64748B; }
.post-title { font-family:var(--font-heading); font-size:18px; font-weight:600; color:#1E3A8A; margin:0 0 10px 0; }
.post-body { font-size:14px; color:#475569; line-height:1.7; }
.analysis-content { min-height:400px; }
.metrics-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }
.metric-card { background:white; border-radius:10px; border:1px solid #DBEAFE; border-left:3px solid #DBEAFE; padding:20px; display:flex; gap:16px; align-items:center; transition:box-shadow 0.2s ease; }
.metric-card:hover { box-shadow:0 4px 16px rgba(30,64,175,0.08); }
.metric-icon { width:56px; height:56px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.metric-num-big { font-family:var(--font-heading,'Fira Code',monospace); font-size:22px; font-weight:700; }
.metric-content { flex:1; }
.metric-label { font-size:12px; color:#64748B; margin-bottom:4px; }
.metric-value { font-family:var(--font-heading,'Fira Code',monospace); font-size:24px; font-weight:600; color:#1E3A8A; }
.stage-value { font-size:18px; }
.section-card { background:white; border:1px solid #DBEAFE; border-radius:10px; padding:20px; margin-bottom:20px; }
.section-header { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.section-icon-svg { width:20px; height:20px; color:#3B82F6; }
.section-title { font-family:var(--font-heading,'Fira Code',monospace); font-size:15px; font-weight:600; color:#1E3A8A; flex:1; }
.evolution-steps { padding:16px 0; }
.analysis-grid { display:grid; grid-template-columns:1fr 360px; gap:20px; align-items:start; }
.signals-table :deep(.el-table__header) { font-weight:600; }
.signals-table :deep(.el-table__row:hover) { background:#f8fafc; }
.signal-score { font-weight:600; color:#f97316; font-family:var(--font-heading,'Fira Code',monospace); }
.comments-grid { display:flex; flex-wrap:wrap; gap:8px; }
.key-comment-item { display:flex; align-items:center; gap:8px; padding:8px 14px; background:#fffbeb; border:1px solid #fde68a; border-radius:8px; font-size:13px; }
.kc-index { width:22px; height:22px; border-radius:50%; background:#f59e0b; color:white; font-size:11px; display:flex; align-items:center; justify-content:center; font-weight:600; font-family:var(--font-heading); }
.kc-id { color:#92400e; font-size:12px; font-family:var(--font-heading); }
.action-row { display:flex; gap:12px; justify-content:center; padding:20px 0; }
</style>
