<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api, type Event, type Report } from '../api/client'
import { Setting, Warning, CircleCheck, Clock, List, OfficeBuilding, ChatLineRound, Select } from '@element-plus/icons-vue'

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
}

watch(eventId, (newId) => {
  if (newId) loadReport()
})

onMounted(() => {
  loadEvents()
  if (eventId.value) loadReport()
})

const evidenceTypes: Record<string, { label: string; color: string }> = {
  '校规': { label: '校规', color: '#3B82F6' },
  '通知': { label: '通知', color: '#D97706' },
  '处置模板': { label: '处置模板', color: '#10b981' },
  '历史案例': { label: '历史案例', color: '#8b5cf6' }
}

const getUrgencyColor = (urgency: string) => {
  if (!urgency) return '#6b7684'
  if (urgency.includes('24小时') || urgency.includes('立即')) return '#ef4444'
  if (urgency.includes('48小时')) return '#f97316'
  return '#f59e0b'
}

const stages = ['监测发现', '初步研判', '证据核查', '响应处置', '效果评估', '归档总结']
</script>

<template>
  <div class="intervention-page">
    <div class="page-header">
      <h1>证据化处置</h1>
      <p class="subtitle">基于知识库检索与结构化研判，生成可执行的温和处置方案</p>
    </div>

    <!-- Event Selector -->
    <div class="selector-bar" v-if="!eventId">
      <div class="selector-hint">
        <Select class="selector-icon" />
        <span>选择一个事件以查看处置方案</span>
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

    <div v-if="eventId && !loading && !report" class="empty-state">
      <el-empty description="该事件暂无处置报告，请先在事件分析页完成分析" :image-size="100" />
    </div>

    <div v-if="report" class="intervention-content">
      <!-- Header: Event Info -->
      <div class="info-bar">
        <div class="info-bar-left">
          <span class="event-id-chip">{{ report.event_id }}</span>
          <span class="event-summary-text">{{ report.event_summary?.slice(0, 80) }}{{ report.event_summary?.length > 80 ? '...' : '' }}</span>
        </div>
        <div class="info-bar-right">
          <el-tag
            :type="report.human_review_required ? 'danger' : 'success'"
            size="large"
          >
            {{ report.human_review_required ? '需人工复核' : '可自动处置' }}
          </el-tag>
        </div>
      </div>

      <!-- Disposition Workflow -->
      <div class="section-card">
        <div class="section-card-header">
          <Clock class="section-icon" />
          <span>24小时处置流程</span>
        </div>
        <div class="workflow-stages">
          <div
            v-for="(stage, index) in stages"
            :key="index"
            class="workflow-stage"
            :class="{ active: index <= 3 }"
          >
            <div class="stage-circle">{{ index + 1 }}</div>
            <div class="stage-label">{{ stage }}</div>
            <div v-if="index < stages.length - 1" class="stage-line"></div>
          </div>
        </div>
      </div>

      <div class="intervention-grid">
        <!-- Left Column: Risk Assessment + Evidence -->
        <div class="intervention-left">
          <!-- Risk Assessment -->
          <div class="section-card">
            <div class="section-card-header">
              <Warning class="section-icon" style="color: #f97316" />
              <span>风险评估摘要</span>
            </div>
            <div class="risk-summary-grid">
              <div class="risk-summary-item">
                <span class="rs-label">风险等级</span>
                <el-tag
                  :color="report.risk_assessment.risk_level === '高' || report.risk_assessment.risk_level === '严重' ? '#ef4444' : report.risk_assessment.risk_level === '中' ? '#f59e0b' : '#10b981'"
                  effect="dark"
                  style="border: none"
                >
                  {{ report.risk_assessment.risk_level }}
                </el-tag>
              </div>
              <div class="risk-summary-item">
                <span class="rs-label">风险分数</span>
                <span class="rs-value-mono">{{ report.risk_assessment.risk_score?.toFixed(1) }}</span>
              </div>
              <div class="risk-summary-item">
                <span class="rs-label">当前阶段</span>
                <span class="rs-value">{{ report.risk_assessment.current_stage }}</span>
              </div>
              <div class="risk-summary-item">
                <span class="rs-label">置信度</span>
                <span class="rs-value-mono">{{ (report.risk_assessment.confidence * 100).toFixed(0) }}%</span>
              </div>
            </div>
            <div class="evolution-path" v-if="report.risk_assessment.evolution_path?.length">
              <span class="ep-label">演化路径：</span>
              <span class="ep-stages">{{ report.risk_assessment.evolution_path.join(' \u2192 ') }}</span>
            </div>
          </div>

          <!-- Evidence Chain -->
          <div class="section-card" v-if="report.evidence?.length">
            <div class="section-card-header">
              <List class="section-icon" style="color: #3B82F6" />
              <span>证据链</span>
              <span class="header-count">{{ report.evidence.length }}</span>
            </div>
            <div class="evidence-list">
              <div
                v-for="(ev, index) in report.evidence"
                :key="index"
                class="evidence-item"
              >
                <div class="evidence-header">
                  <span
                    class="evidence-type-badge"
                    :style="{ background: (evidenceTypes[ev.evidence_type]?.color || '#6b7684') + '18', color: evidenceTypes[ev.evidence_type]?.color || '#6b7684' }"
                  >
                    {{ evidenceTypes[ev.evidence_type]?.label || ev.evidence_type }}
                  </span>
                  <span class="evidence-score">匹配度: {{ ((ev.score || 0) * 100).toFixed(0) }}%</span>
                </div>
                <div class="evidence-title">{{ ev.title }}</div>
                <div class="evidence-content">{{ ev.content?.slice(0, 200) }}{{ ev.content?.length > 200 ? '...' : '' }}</div>
                <div class="evidence-source">来源: {{ ev.source }}</div>
              </div>
            </div>
          </div>

          <!-- Key Comment Explanations -->
          <div class="section-card" v-if="report.key_comment_explanations?.length">
            <div class="section-card-header">
              <ChatLineRound class="section-icon" style="color: #10b981" />
              <span>关键评论分析</span>
            </div>
            <div class="comment-explain-list">
              <div
                v-for="(exp, index) in report.key_comment_explanations"
                :key="index"
                class="comment-explain-item"
              >
                <div class="ce-header">
                  <span class="ce-id">{{ exp.comment_id }}</span>
                  <el-tag size="small" effect="dark">{{ exp.risk_signal }}</el-tag>
                </div>
                <div class="ce-reason">{{ exp.reason }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Intervention Plan -->
        <div class="intervention-right">
          <!-- Official Statement -->
          <div class="section-card highlight-card">
            <div class="section-card-header">
              <OfficeBuilding class="section-icon" style="color: #1E40AF" />
              <span>官方回应建议</span>
            </div>
            <div class="official-statement" v-if="report.intervention.official_statement">
              {{ report.intervention.official_statement }}
            </div>
          </div>

          <!-- Action Items -->
          <div class="section-card">
            <div class="section-card-header">
              <CircleCheck class="section-icon" style="color: #10b981" />
              <span>行动清单</span>
            </div>
            <div class="action-list" v-if="report.intervention.action_items?.length">
              <div
                v-for="(item, index) in report.intervention.action_items"
                :key="index"
                class="action-item"
              >
                <span class="action-num">{{ index + 1 }}</span>
                <span class="action-text">{{ item }}</span>
              </div>
            </div>
          </div>

          <!-- Avoid Phrases -->
          <div class="section-card">
            <div class="section-card-header">
              <Warning class="section-icon" style="color: #DC2626" />
              <span>避免使用的话术</span>
            </div>
            <div class="avoid-list" v-if="report.intervention.avoid_phrases?.length">
              <el-tag
                v-for="(phrase, index) in report.intervention.avoid_phrases"
                :key="index"
                type="danger"
                size="large"
                effect="plain"
                class="avoid-tag"
              >
                {{ phrase }}
              </el-tag>
            </div>
          </div>

          <!-- Responsible Departments + Urgency -->
          <div class="summary-cards">
            <div class="summary-card" v-if="report.intervention.responsible_department?.length">
              <div class="sc-header">责任部门</div>
              <div class="sc-body">
                <el-tag
                  v-for="(dept, index) in report.intervention.responsible_department"
                  :key="index"
                  size="default"
                  type="info"
                  effect="plain"
                  class="dept-tag"
                >
                  {{ dept }}
                </el-tag>
              </div>
            </div>
            <div class="summary-card" v-if="report.intervention.urgency">
              <div class="sc-header">处置时限</div>
              <div class="sc-body">
                <span
                  class="urgency-badge"
                  :style="{ background: getUrgencyColor(report.intervention.urgency) + '18', color: getUrgencyColor(report.intervention.urgency), borderColor: getUrgencyColor(report.intervention.urgency) + '40' }"
                >
                  {{ report.intervention.urgency }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.intervention-page {
  padding: 20px 24px;
  max-width: 1400px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-family: var(--font-heading, 'Fira Code', monospace);
  font-size: 24px;
  font-weight: 600;
  color: #1E3A8A;
  margin: 0 0 6px 0;
}

.subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

/* Event Selector */
.selector-bar {
  background: white;
  border: 2px dashed #DBEAFE;
  border-radius: 10px;
  padding: 32px;
  text-align: center;
}

.selector-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
  color: #64748B;
  font-size: 15px;
}

.selector-icon {
  width: 20px;
  height: 20px;
  color: #3B82F6;
}

.event-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.event-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #DBEAFE;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-family: var(--font-body);
  transition: all 0.15s;
}

.event-chip:hover {
  border-color: #3B82F6;
  background: #eff6ff;
}

.chip-id {
  font-family: var(--font-heading);
  font-size: 12px;
  color: #3B82F6;
  font-weight: 600;
}

.chip-title {
  color: #1e293b;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Info Bar */
.info-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  border: 1px solid #DBEAFE;
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.info-bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.event-id-chip {
  font-family: var(--font-heading);
  font-size: 13px;
  font-weight: 600;
  background: rgba(30, 64, 175, 0.08);
  color: #1E40AF;
  padding: 4px 12px;
  border-radius: 6px;
}

.event-summary-text {
  font-size: 14px;
  color: #475569;
}

/* Section Cards */
.section-card {
  background: white;
  border: 1px solid #DBEAFE;
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 16px;
}

.section-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-family: var(--font-heading, 'Fira Code', monospace);
  font-size: 14px;
  font-weight: 600;
  color: #1E3A8A;
}

.section-icon {
  width: 18px;
  height: 18px;
}

.header-count {
  font-size: 12px;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 10px;
  color: #64748B;
}

/* Workflow */
.workflow-stages {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.workflow-stage {
  display: flex;
  align-items: center;
  flex: 1;
  position: relative;
}

.stage-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  font-family: var(--font-heading);
}

.workflow-stage.active .stage-circle {
  background: #1E40AF;
  color: white;
}

.stage-label {
  font-size: 11px;
  color: #94a3b8;
  margin-left: 8px;
  white-space: nowrap;
}

.workflow-stage.active .stage-label {
  color: #1E40AF;
  font-weight: 600;
}

.stage-line {
  flex: 1;
  height: 2px;
  background: #e2e8f0;
  margin: 0 8px;
  min-width: 16px;
}

.workflow-stage.active + .workflow-stage .stage-line,
.workflow-stage.active .stage-line {
  background: #1E40AF;
}

/* Two column layout */
.intervention-grid {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 20px;
  align-items: start;
}

/* Risk Summary */
.risk-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.risk-summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rs-label {
  font-size: 11px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.rs-value {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.rs-value-mono {
  font-family: var(--font-heading);
  font-size: 20px;
  font-weight: 700;
  color: #1E3A8A;
}

.evolution-path {
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 13px;
}

.ep-label {
  color: #94a3b8;
}

.ep-stages {
  color: #1e293b;
  font-weight: 500;
}

/* Evidence */
.evidence-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.evidence-item {
  padding: 12px;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
}

.evidence-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.evidence-type-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.evidence-score {
  font-size: 11px;
  color: #94a3b8;
  font-family: var(--font-heading);
}

.evidence-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.evidence-content {
  font-size: 13px;
  color: #64748B;
  line-height: 1.6;
  margin-bottom: 4px;
}

.evidence-source {
  font-size: 11px;
  color: #94a3b8;
}

/* Comment Explanations */
.comment-explain-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comment-explain-item {
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.ce-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.ce-id {
  font-family: var(--font-heading);
  font-size: 12px;
  color: #3B82F6;
}

.ce-reason {
  font-size: 13px;
  color: #475569;
  line-height: 1.5;
}

/* Official Statement */
.highlight-card {
  border-color: rgba(30, 64, 175, 0.2);
  background: linear-gradient(135deg, rgba(30, 64, 175, 0.02), rgba(59, 130, 246, 0.03));
}

.official-statement {
  font-size: 14px;
  color: #1e293b;
  line-height: 1.8;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

/* Action Items */
.action-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 10px 12px;
  background: #f0fdf4;
  border-radius: 8px;
  border: 1px solid #bbf7d0;
}

.action-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #10b981;
  color: white;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-family: var(--font-heading);
}

.action-text {
  font-size: 13px;
  color: #166534;
  line-height: 1.5;
}

/* Avoid Phrases */
.avoid-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.avoid-tag {
  font-size: 12px;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.summary-card {
  background: white;
  border: 1px solid #DBEAFE;
  border-radius: 10px;
  padding: 14px 16px;
}

.sc-header {
  font-family: var(--font-heading);
  font-size: 12px;
  color: #64748B;
  margin-bottom: 8px;
  letter-spacing: 0.3px;
}

.sc-body {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.dept-tag {
  font-size: 12px;
}

.urgency-badge {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 14px;
  border: 1px solid;
  border-radius: 8px;
}

.empty-state {
  padding: 60px 0;
}
</style>
