<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { api, type GraphData, type GraphNode, type Event } from "../api/client"
import { Network } from "vis-network"
import { ArrowLeft, Select } from "@element-plus/icons-vue"

const route = useRoute()
const router = useRouter()
const eventId = ref((route.params.id as string) || "")
const graphData = ref<GraphData | null>(null)
const selectedNode = ref<GraphNode | null>(null)
const loading = ref(false)
const containerRef = ref<HTMLElement | null>(null)
let network: Network | null = null

const events = ref<Event[]>([])
const loadingEvents = ref(false)

const showReply = ref(true)
const showTemporal = ref(true)
const showSemantic = ref(true)

const stats = ref({ totalNodes: 0, replyEdges: 0, temporalEdges: 0, semanticEdges: 0, highRiskNodes: 0 })

const loadEvents = async () => {
  loadingEvents.value = true
  try {
    const response = await api.getEvents()
    events.value = response.data.items
  } catch (error) {
    console.error("Failed to load events:", error)
  } finally {
    loadingEvents.value = false
  }
}

const loadGraph = async () => {
  if (!eventId.value) return
  loading.value = true
  try {
    const response = await api.getGraph(eventId.value)
    graphData.value = response.data
    computeStats()
    await nextTick()
    renderGraph()
  } catch (error) {
    console.error("Failed to load graph:", error)
  } finally {
    loading.value = false
  }
}

const selectEvent = (id: string) => {
  eventId.value = id
  loadGraph()
}

const computeStats = () => {
  if (!graphData.value) return
  const nodes = graphData.value.nodes
  const edges = graphData.value.edges
  stats.value = {
    totalNodes: nodes.length,
    replyEdges: edges.filter(e => e.edge_type === "reply").length,
    temporalEdges: edges.filter(e => e.edge_type === "temporal").length,
    semanticEdges: edges.filter(e => e.edge_type === "semantic").length,
    highRiskNodes: nodes.filter(n => n.risk_score > 0.4).length
  }
}

const getVisibleEdges = () => {
  if (!graphData.value) return []
  return graphData.value.edges.filter(e => {
    if (e.edge_type === "reply" && !showReply.value) return false
    if (e.edge_type === "temporal" && !showTemporal.value) return false
    if (e.edge_type === "semantic" && !showSemantic.value) return false
    return true
  })
}

const renderGraph = () => {
  if (!containerRef.value || !graphData.value) return

  const nodes = graphData.value.nodes.map(node => ({
    id: node.node_id,
    label: node.label,
    size: node.size * 1.5,
    font: { size: 12, color: "#ffffff" },
    color: {
      background: node.node_type === "post"
        ? "#1E40AF"
        : node.risk_score > 0.7 ? "#ef4444" : node.risk_score > 0.4 ? "#f59e0b" : "#10b981",
      border: node.node_type === "post" ? "#1e3a8a" : "#ffffff",
      highlight: { background: "#1e3a8a", border: "#1E40AF" }
    },
    borderWidth: 2,
    node_type: node.node_type,
    risk_score: node.risk_score
  }))

  const visibleEdges = getVisibleEdges()
  const edges = visibleEdges.map(edge => ({
    from: edge.source,
    to: edge.target,
    arrows: { to: { enabled: true, scaleFactor: 0.8 } },
    color: {
      color: edge.edge_type === "reply" ? "#64748b"
        : edge.edge_type === "semantic" ? "#8b5cf6"
        : "#cbd5e1",
      highlight: "#1E40AF"
    },
    width: edge.edge_type === "reply" ? 2 : 1,
    smooth: { enabled: true, type: edge.edge_type === "reply" ? "cubicBezier" as const : "continuous" as const, roundness: 0.2 },
    edge_type: edge.edge_type
  }))

  if (network) { network.destroy(); network = null }

  network = new Network(containerRef.value, { nodes, edges }, {
    physics: {
      barnesHut: { gravitationalConstant: -8000, springLength: 180, springConstant: 0.04, damping: 0.3 },
      stabilization: { iterations: 200 }
    },
    interaction: { hover: true, tooltipDelay: 100, zoomView: true, dragView: true }
  })

  network.on("click", (params: any) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = graphData.value!.nodes.find(n => n.node_id === nodeId)
      selectedNode.value = node || null
    } else {
      selectedNode.value = null
    }
  })
}

watch([showReply, showTemporal, showSemantic], () => {
  renderGraph()
})

onMounted(() => {
  loadEvents()
  if (eventId.value) loadGraph()
})

onUnmounted(() => {
  if (network) { network.destroy(); network = null }
})
</script>

<template>
  <div class="comment-graph">
    <div class="page-header">
      <h1>评论图谱</h1>
      <p class="subtitle">评论链建模：回复边、时间线边、语义边三维可视化</p>
      <el-tag v-if="eventId" type="info" size="large">{{ eventId }}</el-tag>
    </div>

    <!-- Event Selector when no ID -->
    <div class="selector-bar" v-if="!eventId">
      <div class="selector-hint">
        <Select class="selector-icon" />
        <span>选择一个事件查看评论链图谱</span>
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

    <template v-if="eventId">
      <!-- edge toggles -->
      <div class="toggle-bar">
        <el-checkbox v-model="showReply" size="large" border>
          <span class="toggle-label">
            <span class="edge-dot" style="background: #64748b"></span> 回复边
            <span class="toggle-count">{{ stats.replyEdges }}</span>
          </span>
        </el-checkbox>
        <el-checkbox v-model="showTemporal" size="large" border>
          <span class="toggle-label">
            <span class="edge-dot" style="background: #cbd5e1"></span> 时间线边
            <span class="toggle-count">{{ stats.temporalEdges }}</span>
          </span>
        </el-checkbox>
        <el-checkbox v-model="showSemantic" size="large" border>
          <span class="toggle-label">
            <span class="edge-dot" style="background: #8b5cf6"></span> 语义边
            <span class="toggle-count">{{ stats.semanticEdges }}</span>
          </span>
        </el-checkbox>
      </div>

      <!-- legend row -->
      <div class="legend-bar">
        <span class="legend-item"><span class="legend-node" style="background: #1E40AF"></span> 主贴</span>
        <span class="legend-item"><span class="legend-node" style="background: #ef4444"></span> 高风险(&gt;0.7)</span>
        <span class="legend-item"><span class="legend-node" style="background: #f59e0b"></span> 中风险(&gt;0.4)</span>
        <span class="legend-item"><span class="legend-node" style="background: #10b981"></span> 低风险</span>
      </div>

      <div v-loading="loading">
        <div ref="containerRef" class="graph-container" />
      </div>

      <div class="info-panel">
        <div class="stats-section">
          <div class="stat-item">
            <span class="stat-num">{{ stats.totalNodes }}</span>
            <span class="stat-text">节点总数</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ stats.replyEdges }}</span>
            <span class="stat-text">回复边</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ stats.temporalEdges }}</span>
            <span class="stat-text">时间边</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ stats.semanticEdges }}</span>
            <span class="stat-text">语义边</span>
          </div>
          <div class="stat-item stat-highlight">
            <span class="stat-num">{{ stats.highRiskNodes }}</span>
            <span class="stat-text">中高风险节点</span>
          </div>
        </div>

        <div class="node-detail" v-if="selectedNode">
          <div class="node-detail-header">节点详情</div>
          <div class="node-detail-body">
            <div class="nd-row"><span class="nd-label">ID</span><span class="nd-value">{{ selectedNode.node_id }}</span></div>
            <div class="nd-row"><span class="nd-label">标签</span><span class="nd-value">{{ selectedNode.label }}</span></div>
            <div class="nd-row"><span class="nd-label">类型</span>
              <el-tag size="small" :type="selectedNode.node_type === 'post' ? 'info' : ''">
                {{ selectedNode.node_type === 'post' ? '主贴' : '评论' }}
              </el-tag>
            </div>
            <div class="nd-row">
              <span class="nd-label">风险分</span>
              <span class="nd-value" :style="{ color: selectedNode.risk_score > 0.7 ? '#ef4444' : selectedNode.risk_score > 0.4 ? '#f59e0b' : '#10b981', fontWeight: '600' }">
                {{ selectedNode.risk_score.toFixed(2) }}
              </span>
            </div>
          </div>
        </div>
        <div class="node-detail node-detail-empty" v-else>
          <span class="empty-hint">点击图谱节点查看详情</span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.comment-graph { max-width: 1400px; margin: 0 auto; padding: 16px 20px; }
.page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.page-header h1 { font-family: var(--font-heading, 'Fira Code', monospace); font-size: 24px; font-weight: 600; color: #1E3A8A; margin: 0; }
.subtitle { font-size: 14px; color: #64748B; margin: 0; }

.selector-bar {
  background: white; border: 2px dashed #DBEAFE; border-radius: 10px; padding: 24px; text-align: center;
}
.selector-hint { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 20px; color: #64748B; font-size: 15px; }
.selector-icon { width: 20px; height: 20px; color: #3B82F6; }
.event-chips { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
.event-chip {
  display: flex; align-items: center; gap: 8px; padding: 8px 16px;
  border: 1px solid #DBEAFE; border-radius: 8px; background: white;
  cursor: pointer; font-size: 13px; transition: all 0.15s;
}
.event-chip:hover { border-color: #3B82F6; background: #eff6ff; }
.chip-id { font-family: var(--font-heading); font-size: 12px; color: #3B82F6; font-weight: 600; }
.chip-title { color: #1e293b; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.toggle-bar { display: flex; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.toggle-bar :deep(.el-checkbox) { padding: 8px 16px; border-radius: 8px; border: 1px solid #e3e8ef; background: white; transition: all 0.2s ease; }
.toggle-bar :deep(.el-checkbox.is-checked) { border-color: #1E40AF; background: #eff6ff; }
.toggle-label { display: flex; align-items: center; gap: 8px; }
.edge-dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.toggle-count { font-size: 12px; color: #64748B; background: #f1f5f9; padding: 2px 8px; border-radius: 10px; }

.legend-bar { display: flex; gap: 20px; margin-bottom: 12px; font-size: 13px; color: #64748B; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-node { width: 14px; height: 14px; border-radius: 50%; display: inline-block; }

.graph-container {
  width: 100%; height: 420px; background: white; border-radius: 10px;
  border: 1px solid #DBEAFE; margin-bottom: 16px;
}

.info-panel { display: grid; grid-template-columns: 1fr 280px; gap: 16px; }
.stats-section {
  display: flex; gap: 16px; flex-wrap: wrap;
  background: white; border-radius: 10px; border: 1px solid #DBEAFE; padding: 16px 20px;
}
.stat-item { text-align: center; min-width: 80px; }
.stat-num { display: block; font-family: var(--font-heading); font-size: 24px; font-weight: 600; color: #1E3A8A; }
.stat-text { font-size: 12px; color: #64748B; }
.stat-highlight .stat-num { color: #ef4444; }

.node-detail { background: white; border-radius: 10px; border: 1px solid #DBEAFE; padding: 16px; }
.node-detail-empty { display: flex; align-items: center; justify-content: center; }
.empty-hint { font-size: 13px; color: #c0c4cc; }
.node-detail-header { font-size: 15px; font-weight: 600; color: #1E3A8A; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f1f5f9; }
.node-detail-body { display: flex; flex-direction: column; gap: 8px; }
.nd-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.nd-label { color: #64748B; }
.nd-value { color: #1E3A8A; font-weight: 500; word-break: break-all; text-align: right; max-width: 160px; }
</style>
