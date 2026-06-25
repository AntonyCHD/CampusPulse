<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from "vue"
import { useRouter } from "vue-router"
import { api, type Event, type DashboardSummary } from "../api/client"
import { Search, ArrowRight, ArrowLeft, ArrowRight as ArrowRightIcon } from "@element-plus/icons-vue"
import * as echarts from "echarts"

const router = useRouter()
const events = ref<Event[]>([])
const summary = ref<DashboardSummary | null>(null)
const loading = ref(false)
const riskFilter = ref("")
const typeFilter = ref("")
const searchQuery = ref("")

let riskDistChart: echarts.ECharts | null = null
let typeDistChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// --- Marquee / Carousel ---
const marqueePaused = ref(false)
const marqueeRef = ref<HTMLElement | null>(null)
let marqueeInterval: ReturnType<typeof setInterval> | null = null
const marqueeScrollPos = ref(0)
const MARQUEE_SPEED = 1.2 // px per frame

const loadEvents = async () => {
  loading.value = true
  try {
    const response = await api.getEvents({
      risk_level: riskFilter.value || undefined,
      event_type: typeFilter.value || undefined
    })
    events.value = response.data.items
    summary.value = response.data.summary
    await nextTick()
    renderCharts()
    startMarquee()
  } catch (error) {
    console.error("Failed to load events:", error)
  } finally {
    loading.value = false
  }
}

const startMarquee = () => {
  stopMarquee()
  marqueeScrollPos.value = 0
  marqueeInterval = setInterval(() => {
    if (marqueePaused.value) return
    const el = marqueeRef.value
    if (!el) return
    const track = el.querySelector(".marquee-track") as HTMLElement
    if (!track) return
    marqueeScrollPos.value += MARQUEE_SPEED
    const maxScroll = track.scrollWidth - el.clientWidth
    if (marqueeScrollPos.value >= maxScroll) {
      marqueeScrollPos.value = 0
    }
    track.style.transform = `translateX(${-marqueeScrollPos.value}px)`
  }, 16) // ~60fps
}

const stopMarquee = () => {
  if (marqueeInterval) { clearInterval(marqueeInterval); marqueeInterval = null }
}

// Highlighted events for marquee: pick highest risk first, then most commented
const marqueeEvents = computed(() => {
  const riskOrder: Record<string, number> = { "严重": 0, "高": 1, "中": 2, "低": 3 }
  return [...events.value]
    .filter(e => e.risk_level)
    .sort((a, b) => (riskOrder[a.risk_level || "低"] ?? 99) - (riskOrder[b.risk_level || "低"] ?? 99))
    .slice(0, 12)
})

const filteredEvents = computed(() => {
  if (!searchQuery.value) return events.value
  const q = searchQuery.value.toLowerCase()
  return events.value.filter(e =>
    e.title.toLowerCase().includes(q) || e.event_id.toLowerCase().includes(q)
  )
})

const highRiskEvents = computed(() =>
  filteredEvents.value.filter(e => e.risk_level === "高" || e.risk_level === "严重")
)

const getRiskColor = (level?: string) => {
  const colors: Record<string, string> = {
    "低": "#10b981", "中": "#f59e0b", "高": "#f97316", "严重": "#ef4444"
  }
  return colors[level || ""] || "#6b7684"
}

const goToEvent = (eventId: string) => { router.push("/event/" + eventId) }

const renderCharts = () => {
  if (!summary.value) return
  const riskDistDom = document.getElementById("risk-dist-chart")
  if (riskDistDom && summary.value.risk_distribution) {
    if (!riskDistChart) riskDistChart = echarts.init(riskDistDom)
    const dist = summary.value.risk_distribution
    riskDistChart.setOption({
      tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
      series: [{
        type: "pie", radius: ["52%", "80%"], center: ["50%", "50%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: "bold" } },
        data: Object.entries(dist).map(([name, value]) => {
          const cm: Record<string, string> = { "低": "#10b981", "中": "#f59e0b", "高": "#f97316", "严重": "#ef4444" }
          return { name, value, itemStyle: { color: cm[name] || "#6b7684" } }
        })
      }]
    })
  }
  const typeDistDom = document.getElementById("type-dist-chart")
  if (typeDistDom && summary.value.event_type_distribution) {
    if (!typeDistChart) typeDistChart = echarts.init(typeDistDom)
    const dist = summary.value.event_type_distribution
    typeDistChart.setOption({
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      grid: { left: "3%", right: "8%", bottom: "3%", top: "8%", containLabel: true },
      xAxis: { type: "value", axisLabel: { fontSize: 10 } },
      yAxis: { type: "category", data: Object.keys(dist), axisLabel: { fontSize: 11 }, inverse: true },
      series: [{
        type: "bar", data: Object.values(dist), barWidth: 16,
        itemStyle: { borderRadius: [0, 6, 6, 0], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: "#1E40AF" }, { offset: 1, color: "#3B82F6" }]) }
      }]
    })
  }
  const trendDom = document.getElementById("trend-chart")
  if (trendDom && summary.value.risk_trend?.length) {
    if (!trendChart) trendChart = echarts.init(trendDom)
    const trend = summary.value.risk_trend
    trendChart.setOption({
      tooltip: { trigger: "axis" },
      legend: { data: ["风险分数", "事件数"], bottom: 0, textStyle: { fontSize: 11 } },
      grid: { left: "3%", right: "4%", top: "8%", bottom: "12%", containLabel: true },
      xAxis: { type: "category", data: trend.map((t: any) => t.date), axisLabel: { rotate: 35, fontSize: 10 } },
      yAxis: [{ type: "value", name: "分数", nameTextStyle: { fontSize: 10 }, axisLabel: { fontSize: 10 } }, { type: "value", name: "数量", nameTextStyle: { fontSize: 10 }, axisLabel: { fontSize: 10 } }],
      series: [
        { name: "风险分数", type: "line", smooth: true, data: trend.map((t: any) => t.avg_risk_score), itemStyle: { color: "#DC2626" }, lineStyle: { width: 2 }, areaStyle: { color: "rgba(220,38,38,0.08)" } },
        { name: "事件数", type: "bar", yAxisIndex: 1, data: trend.map((t: any) => t.event_count), barWidth: 12, itemStyle: { borderRadius: [3,3,0,0], color: "rgba(30,64,175,0.4)" } }
      ]
    })
  }
}

const handleResize = () => { riskDistChart?.resize(); typeDistChart?.resize(); trendChart?.resize() }

onMounted(() => { loadEvents(); window.addEventListener("resize", handleResize) })
onUnmounted(() => {
  window.removeEventListener("resize", handleResize)
  riskDistChart?.dispose(); typeDistChart?.dispose(); trendChart?.dispose()
  stopMarquee()
})
</script>

<template>
  <div class="event-overview">
    <!-- Filters Row -->
    <div class="filters-row">
      <el-input v-model="searchQuery" placeholder="搜索事件标题或ID" :prefix-icon="Search" clearable class="search-input" />
      <el-select v-model="riskFilter" placeholder="风险等级" clearable @change="loadEvents" class="filter-select">
        <el-option label="低风险" value="低" /><el-option label="中风险" value="中" />
        <el-option label="高风险" value="高" /><el-option label="严重" value="严重" />
      </el-select>
      <el-select v-model="typeFilter" placeholder="事件类型" clearable @change="loadEvents" class="filter-select">
        <el-option label="学术" value="学术" /><el-option label="生活" value="生活" />
        <el-option label="安全" value="安全" /><el-option label="管理" value="管理" />
        <el-option label="舆论" value="舆论" />
      </el-select>
      <span class="filter-brief" v-if="summary">
        共 {{ filteredEvents.length }} 事件 · {{ summary.high_risk_events }} 高风险
      </span>
    </div>

    <!-- Summary Metrics Row -->
    <div class="metrics-row" v-if="summary">
      <div class="metric-inline">
        <span class="mi-value">{{ summary.total_events }}</span>
        <span class="mi-label">累计事件</span>
      </div>
      <div class="metric-inline">
        <span class="mi-value">{{ summary.today_events }}</span>
        <span class="mi-label">今日新增</span>
      </div>
      <div class="metric-inline metric-inline-highlight">
        <span class="mi-value" style="color:#DC2626">{{ summary.high_risk_events }}</span>
        <span class="mi-label">高风险</span>
      </div>
    </div>

    <!-- Marquee Carousel -->
    <div
      v-if="marqueeEvents.length > 0"
      ref="marqueeRef"
      class="marquee-container"
      @mouseenter="marqueePaused = true"
      @mouseleave="marqueePaused = false"
    >
      <div class="marquee-label">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        <span>实时关注</span>
      </div>
      <div class="marquee-track">
        <div
          v-for="event in marqueeEvents"
          :key="event.event_id"
          class="marquee-card"
          :style="{ borderLeftColor: getRiskColor(event.risk_level) }"
          @click="goToEvent(event.event_id)"
        >
          <span class="marquee-card-risk" :style="{ color: getRiskColor(event.risk_level) }">
            {{ event.risk_level }}
          </span>
          <span class="marquee-card-title">{{ event.title }}</span>
          <span class="marquee-card-type">{{ event.event_type }}</span>
        </div>
        <!-- Duplicate for seamless loop -->
        <div
          v-for="event in marqueeEvents"
          :key="event.event_id + '-dup'"
          class="marquee-card"
          :style="{ borderLeftColor: getRiskColor(event.risk_level) }"
          @click="goToEvent(event.event_id)"
        >
          <span class="marquee-card-risk" :style="{ color: getRiskColor(event.risk_level) }">
            {{ event.risk_level }}
          </span>
          <span class="marquee-card-title">{{ event.title }}</span>
          <span class="marquee-card-type">{{ event.event_type }}</span>
        </div>
      </div>
      <div class="marquee-fade marquee-fade-left"></div>
      <div class="marquee-fade marquee-fade-right"></div>
    </div>

    <!-- Dashboard Grid: Trend + Charts -->
    <div class="dashboard-grid">
      <div class="trend-panel" v-if="summary?.risk_trend?.length">
        <div class="chart-card trend-card">
          <div class="chart-card-header">风险趋势</div>
          <div id="trend-chart" class="chart-box chart-box-tall"></div>
        </div>
      </div>

      <div class="charts-panel">
        <div class="chart-card">
          <div class="chart-card-header">风险分布</div>
          <div id="risk-dist-chart" class="chart-box"></div>
        </div>
        <div class="chart-card">
          <div class="chart-card-header">事件类型</div>
          <div id="type-dist-chart" class="chart-box"></div>
        </div>
        <div class="chart-card">
          <div class="chart-card-header">高风险关注</div>
          <div class="high-risk-list">
            <div v-for="event in highRiskEvents.slice(0, 5)" :key="event.event_id" class="high-risk-item" @click="goToEvent(event.event_id)">
              <span class="hr-badge" :style="{ background: getRiskColor(event.risk_level) + '18', color: getRiskColor(event.risk_level) }">{{ event.risk_level }}</span>
              <span class="hr-title">{{ event.title }}</span>
              <span class="hr-comments">{{ event.comment_count }}评</span>
            </div>
            <div v-if="highRiskEvents.length === 0" class="no-risk-msg">暂无高风险事件</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Events List Full Width -->
    <div class="events-section">
      <div class="events-panel">
        <div class="panel-header">
          <h3>事件列表</h3>
          <span class="panel-count">{{ filteredEvents.length }}</span>
        </div>
        <div class="event-cards-list" v-loading="loading">
          <div v-for="event in filteredEvents" :key="event.event_id" class="event-row" @click="goToEvent(event.event_id)">
            <div class="event-row-left">
              <span class="risk-dot" :style="{ background: getRiskColor(event.risk_level) }" :title="event.risk_level"></span>
              <div class="event-row-info">
                <div class="event-row-title">{{ event.title }}</div>
                <div class="event-row-meta">
                  <span class="meta-tag">{{ event.event_type }}</span>
                  <span>{{ event.comment_count }} 评论</span>
                  <span>{{ event.like_count }} 点赞</span>
                </div>
              </div>
            </div>
            <div class="event-row-right">
              <el-tag size="small" effect="dark" :color="getRiskColor(event.risk_level)" class="risk-tag">{{ event.risk_level || '-' }}</el-tag>
              <span class="event-time">{{ event.created_at?.slice(0, 10) }}</span>
              <el-icon class="row-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
          <el-empty v-if="!loading && filteredEvents.length === 0" description="暂无事件数据" :image-size="80" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.event-overview { padding: 16px 20px; max-width: 1600px; }

.filters-row { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.search-input { max-width: 300px; }
.filter-select { width: 130px; }
.filter-brief { font-size: 13px; color: #64748B; margin-left: auto; white-space: nowrap; }

.metrics-row { display: flex; gap: 24px; margin-bottom: 16px; }
.metric-inline { display: flex; align-items: baseline; gap: 8px; }
.mi-value { font-family: var(--font-heading, 'Fira Code', monospace); font-size: 22px; font-weight: 600; color: #1E3A8A; }
.mi-label { font-size: 13px; color: #64748B; }

/* ===== Marquee Carousel ===== */
.marquee-container {
  position: relative;
  display: flex;
  align-items: center;
  height: 52px;
  margin-bottom: 20px;
  background: white;
  border: 1px solid var(--color-border, #DBEAFE);
  border-radius: 10px;
  overflow: hidden;
}

.marquee-label {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  height: 100%;
  flex-shrink: 0;
  background: #f0f4ff;
  border-right: 1px solid var(--color-border, #DBEAFE);
  font-family: var(--font-heading, 'Fira Code', monospace);
  font-size: 12px;
  font-weight: 600;
  color: #1E40AF;
  letter-spacing: 0.4px;
}

.marquee-track {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 8px;
  white-space: nowrap;
  will-change: transform;
}

.marquee-card {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: #f8fafc;
  border-left: 2.5px solid #DBEAFE;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s;
  flex-shrink: 0;
}

.marquee-card:hover {
  background: #eff6ff;
  box-shadow: 0 1px 6px rgba(30, 64, 175, 0.08);
}

.marquee-card-risk {
  font-family: var(--font-heading, 'Fira Code', monospace);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.marquee-card-title {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.marquee-card-type {
  font-size: 11px;
  color: #94a3b8;
  padding: 1px 8px;
  background: rgba(30, 64, 175, 0.05);
  border-radius: 3px;
}

.marquee-fade {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 40px;
  z-index: 1;
  pointer-events: none;
}

.marquee-fade-left {
  left: 108px; /* after the label */
  background: linear-gradient(to right, white 0%, transparent 100%);
}

.marquee-fade-right {
  right: 0;
  background: linear-gradient(to left, white 0%, transparent 100%);
}

/* ===== Dashboard Grid ===== */
.dashboard-grid { display: grid; grid-template-columns: 1fr 360px; gap: 20px; margin-bottom: 20px; }

.events-panel { background: white; border: 1px solid var(--color-border, #DBEAFE); border-radius: 10px; overflow: hidden; }
.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; border-bottom: 1px solid #f1f5f9; }
.panel-header h3 { font-family: var(--font-heading); font-size: 14px; font-weight: 600; color: #1E3A8A; margin: 0; }
.panel-count { font-size: 12px; color: #64748B; background: #f1f5f9; padding: 2px 10px; border-radius: 10px; }
.event-cards-list { max-height: 640px; overflow-y: auto; }

.event-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 20px; border-bottom: 1px solid #f8fafc;
  cursor: pointer; transition: background 0.15s;
}
.event-row:hover { background: #f8fafc; }
.event-row:last-child { border-bottom: none; }
.event-row-left { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.risk-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.event-row-info { min-width: 0; }
.event-row-title { font-size: 14px; font-weight: 500; color: #1e293b; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.event-row-meta { display: flex; gap: 12px; font-size: 12px; color: #94a3b8; }
.meta-tag { color: #3B82F6; font-weight: 500; }
.event-row-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; margin-left: 16px; }
.risk-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
.event-time { font-size: 12px; color: #94a3b8; font-family: var(--font-heading); }
.row-arrow { color: #cbd5e1; font-size: 14px; }
.event-row:hover .row-arrow { color: #3B82F6; }

.charts-panel { display: flex; flex-direction: column; gap: 14px; }
.chart-card { background: white; border: 1px solid var(--color-border, #DBEAFE); border-radius: 10px; padding: 14px 18px; }
.chart-card.full-width { width: 100%; }
.chart-card-header { font-family: var(--font-heading); font-size: 12px; font-weight: 600; color: #1E3A8A; margin-bottom: 6px; letter-spacing: 0.3px; }
.chart-box { height: 180px; }
.chart-box-tall { height: 280px; }

.high-risk-list { display: flex; flex-direction: column; gap: 6px; }
.high-risk-item { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 6px; cursor: pointer; transition: background 0.15s; border: 1px solid transparent; }
.high-risk-item:hover { background: #fef2f2; border-color: #fecaca; }
.hr-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; flex-shrink: 0; }
.hr-title { font-size: 13px; color: #1e293b; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hr-comments { font-size: 11px; color: #94a3b8; flex-shrink: 0; }
.no-risk-msg { font-size: 13px; color: #94a3b8; text-align: center; padding: 16px 0; }

/* Trend panel in dashboard grid */
.trend-panel {
  background: white;
  border: 1px solid var(--color-border, #DBEAFE);
  border-radius: 10px;
  overflow: hidden;
}

.trend-card {
  border: none;
  border-radius: 0;
  padding: 14px 18px;
  height: 100%;
}

.trend-card .chart-box-tall {
  height: calc(100% - 30px);
  min-height: 420px;
}

/* Events Section full width */
.events-section {
  margin-top: 20px;
}
</style>