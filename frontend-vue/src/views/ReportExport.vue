<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api, type Event, type Report } from '../api/client'
import { Download, Select } from '@element-plus/icons-vue'

const route = useRoute()
const eventId = ref((route.params.id as string) || '')
const report = ref<Report | null>(null)
const events = ref<Event[]>([])
const loading = ref(false)
const loadingEvents = ref(false)

const loadEvents = async () => {
  loadingEvents.value = true
  try {
    const response = await api.getEvents()
    events.value = response.data.items
  } catch (error) {
    console.error('Failed to load events:', error)
  } finally {
    loadingEvents.value = false
  }
}

const loadReport = async () => {
  if (!eventId.value) return
  loading.value = true
  try {
    const response = await api.getReport(eventId.value)
    report.value = response.data
  } catch (error) {
    console.error('Failed to load report:', error)
    report.value = null
  } finally {
    loading.value = false
  }
}

const selectEvent = (id: string) => {
  eventId.value = id
  loadReport()
}

const exportMarkdown = async () => {
  try {
    const response = await api.exportReport(eventId.value, 'md')
    const content = (response.data as any).content || JSON.stringify(response.data)
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'report_' + eventId.value + '.md'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export failed:', error)
  }
}

const getRiskColor = (level: string) => {
  const colors: Record<string, string> = {
    '低': '#10b981', '中': '#f59e0b', '高': '#f97316', '严重': '#ef4444'
  }
  return colors[level] || '#6b7684'
}

onMounted(() => {
  loadEvents()
  if (eventId.value) loadReport()
})
</script>

<template>
  <div class="report-export">
    <div class="page-header">
      <h1>报告导出</h1>
      <p class="subtitle">生成结构化分析报告，支持 Markdown / PDF 导出</p>
      <el-button v-if="report" :icon="Download" type="primary" @click="exportMarkdown" class="export-btn">
        导出 Markdown
      </el-button>
    </div>

    <!-- Event Selector -->
    <div class="selector-bar" v-if="!eventId">
      <div class="selector-hint">
        <Select class="selector-icon" />
        <span>选择一个事件以生成分析报告</span>
      </div>
      <div class="event-chips" v-loading="loadingEvents">
        <button
          v-for="event in events.slice(0, 8)"
          :key="event.event_id"
          class="event-chip"
          @click="selectEvent(event.event_id)"
        >
          <span class="chip-id">{{ event.event_id }}</span>
          <span class="chip-title">{{ event.title }}</span>
        </button>
      </div>
    </div>

    <div v-loading="loading">
      <div v-if="report">
        <!-- Event Summary -->
        <div class="section-card">
          <div class="section-card-header">事件概况</div>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="事件 ID">
              <span class="mono-text">{{ report.event_id }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="事件摘要">{{ report.event_summary }}</el-descriptions-item>
            <el-descriptions-item label="生成时间">
              <span class="mono-text">{{ report.generated_at }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Risk Assessment -->
        <div class="section-card">
          <div class="section-card-header">风险评估</div>
          <el-row :gutter="20" style="margin-bottom: 16px">
            <el-col :span="6">
              <div class="kpi-card">
                <span class="kpi-label">风险等级</span>
                <el-tag :color="getRiskColor(report.risk_assessment.risk_level)" effect="dark" style="border:none; font-size: 16px">
                  {{ report.risk_assessment.risk_level }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="kpi-card">
                <span class="kpi-label">风险分数</span>
                <span class="kpi-value">{{ report.risk_assessment.risk_score?.toFixed(1) }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="kpi-card">
                <span class="kpi-label">当前阶段</span>
                <span class="kpi-value">{{ report.risk_assessment.current_stage }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="kpi-card">
                <span class="kpi-label">置信度</span>
                <span class="kpi-value mono-text">{{ (report.risk_assessment.confidence * 100).toFixed(0) }}%</span>
              </div>
            </el-col>
          </el-row>
          <el-divider />
          <div class="evolution-line">
            <span class="ev-label">演化路径</span>
            <span class="ev-path">{{ report.risk_assessment.evolution_path?.join(' \u2192 ') }}</span>
          </div>
        </div>

        <!-- Key Findings -->
        <div class="section-card">
          <div class="section-card-header">关键发现</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="finding-card">
                <div class="finding-num">{{ report.key_findings.key_comments?.length || 0 }}</div>
                <div class="finding-label">关键评论</div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="finding-card">
                <div class="finding-num" style="color: #f97316">{{ report.key_findings.risk_signals?.length || 0 }}</div>
                <div class="finding-label">风险信号</div>
              </div>
            </el-col>
          </el-row>
          <div class="key-comments-list" v-if="report.key_findings.key_comments?.length" style="margin-top: 16px">
            <div v-for="(cid, idx) in report.key_findings.key_comments" :key="idx" class="key-comment-tag">
              {{ cid }}
            </div>
          </div>
        </div>

        <!-- Intervention -->
        <div class="section-card">
          <div class="section-card-header">处置建议</div>
          <el-alert :title="report.intervention.summary" type="warning" :closable="false" style="margin-bottom: 16px" />
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="官方回应">
              {{ report.intervention.official_statement }}
            </el-descriptions-item>
            <el-descriptions-item label="行动清单">
              <ul style="margin: 0; padding-left: 20px">
                <li v-for="(item, index) in report.intervention.action_items" :key="index">{{ item }}</li>
              </ul>
            </el-descriptions-item>
            <el-descriptions-item label="避免话术">
              <el-tag v-for="(phrase, index) in report.intervention.avoid_phrases" :key="index"
                      type="danger" size="small" style="margin: 2px">
                {{ phrase }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="负责部门">
              {{ report.intervention.responsible_department?.join(', ') }}
            </el-descriptions-item>
            <el-descriptions-item label="处置时限">
              <el-tag :type="report.intervention.urgency?.includes('24') ? 'danger' : 'info'">
                {{ report.intervention.urgency }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="人工复核">
              <el-tag :type="report.human_review_required ? 'danger' : 'success'">
                {{ report.human_review_required ? '需要' : '不需要' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.report-export { max-width: 1400px; margin: 0 auto; padding: 16px 20px; }

.page-header {
  display: flex; align-items: center; gap: 16px; margin-bottom: 24px;
}
.page-header h1 {
  font-family: var(--font-heading, 'Fira Code', monospace);
  font-size: 24px; font-weight: 600; color: #1E3A8A; margin: 0;
}
.subtitle { font-size: 14px; color: #64748B; margin: 0; flex: 1; }
.export-btn { flex-shrink: 0; }

.selector-bar {
  background: white; border: 2px dashed #DBEAFE; border-radius: 12px; padding: 32px; text-align: center;
}
.selector-hint { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 20px; color: #64748B; font-size: 15px; }
.selector-icon { width: 20px; height: 20px; color: #3B82F6; }
.event-chips { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
.event-chip {
  display: flex; align-items: center; gap: 8px; padding: 8px 16px;
  border: 1px solid #DBEAFE; border-radius: 8px; background: white;
  cursor: pointer; font-size: 13px; font-family: var(--font-body); transition: all 0.15s;
}
.event-chip:hover { border-color: #3B82F6; background: #eff6ff; }
.chip-id { font-family: var(--font-heading); font-size: 12px; color: #3B82F6; font-weight: 600; }
.chip-title { color: #1e293b; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.section-card {
  background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px;
}
.section-card-header {
  font-family: var(--font-heading); font-size: 14px; font-weight: 600; color: #1E3A8A;
  margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9;
}

.mono-text { font-family: var(--font-heading); }

.kpi-card {
  display: flex; flex-direction: column; gap: 4px;
  padding: 12px; background: #f8fafc; border-radius: 8px;
}
.kpi-label { font-size: 12px; color: #64748B; }
.kpi-value {
  font-family: var(--font-heading); font-size: 20px; font-weight: 700; color: #1E3A8A;
}

.evolution-line {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; background: #f8fafc; border-radius: 8px;
}
.ev-label { font-size: 13px; color: #64748B; flex-shrink: 0; }
.ev-path { font-size: 14px; color: #1E3A8A; font-weight: 500; }

.finding-card {
  padding: 16px; background: #f8fafc; border-radius: 8px; text-align: center;
}
.finding-num { font-family: var(--font-heading); font-size: 32px; font-weight: 700; color: #1E3A8A; }
.finding-label { font-size: 13px; color: #64748B; margin-top: 4px; }

.key-comments-list { display: flex; flex-wrap: wrap; gap: 8px; }
.key-comment-tag {
  font-family: var(--font-heading); font-size: 12px; padding: 4px 12px;
  background: #fffbeb; border: 1px solid #fde68a; color: #92400e; border-radius: 6px;
}
</style>
