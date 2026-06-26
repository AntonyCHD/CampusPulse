<script setup lang="ts">
import { ref, computed } from "vue"
import { api } from "../api/client"
import SkeletonPresets from "../components/SkeletonPresets.vue"

const eventId = ref("E2889899")
const loading = ref(false)
const result = ref<any>(null)

const methods = ref({
  keyword: true,
  sentiment: true,
  comment_chain: true
})

const runComparison = async () => {
  loading.value = true
  try {
    const response = await api.compareBaseline(eventId.value, "all")
    result.value = response.data
  } catch (error) {
    console.error("Comparison failed:", error)
  } finally {
    loading.value = false
  }
}

const getMethodLabel = (method: string) => {
  const labels: Record<string, string> = {
    comment_chain_method: "评论链演化法（本系统）",
    keyword_method: "关键词法",
    sentiment_method: "情感分析法"
  }
  return labels[method] || method
}

const getRiskColor = (level: string) => {
  const colors: Record<string, string> = {
    "低": "#10b981", "中": "#f59e0b", "高": "#f97316", "严重": "#ef4444"
  }
  return colors[level] || "#6b7684"
}

const enabledMethods = computed(() => {
  const map: Record<string, string> = {
    keyword: "keyword_method",
    sentiment: "sentiment_method",
    comment_chain: "comment_chain_method"
  }
  return Object.entries(methods.value).filter(([_, v]) => v).map(([k]) => map[k])
})
</script>

<template>
  <div class="comparison">
    <div class="page-header">
      <h1>方法对比</h1>
      <p class="subtitle">不同分析方法的输出对比</p>
    </div>

    <el-card shadow="never" class="control-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="7">
          <el-input v-model="eventId" placeholder="输入事件ID" size="large" clearable>
            <template #prepend>事件ID</template>
          </el-input>
        </el-col>
        <el-col :span="11">
          <el-checkbox v-model="methods.keyword" label="关键词法" size="large" />
          <el-checkbox v-model="methods.sentiment" label="情感分析法" size="large" />
          <el-checkbox v-model="methods.comment_chain" label="评论链演化法" size="large" />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" size="large" :loading="loading" @click="runComparison" style="width: 100%">
            运行对比
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="results-area">
      <div class="results-grid">
        <div v-for="i in 3" :key="i" class="sk-result-card" :style="{ animationDelay: i * 50 + 'ms' }">
          <div class="sk-shimmer sk-result-header"></div>
          <div class="sk-shimmer sk-result-body"></div>
          <div class="sk-shimmer sk-result-detail"></div>
        </div>
      </div>
    </div>

    <!-- Results -->
    <div v-else class="results-area">
      <el-empty v-if="!result" description="输入事件ID并点击运行对比" :image-size="120" />
      <div v-else class="results-grid">
        <el-card
          v-for="method in enabledMethods"
          :key="method"
          shadow="never"
          class="method-card"
          :class="{ 'method-highlight': method === 'comment_chain_method' }"
        >
          <template #header>
            <div class="method-header">
              <strong class="method-name">{{ getMethodLabel(method) }}</strong>
              <el-tag
                v-if="result[method]?.risk_level"
                size="small"
                effect="dark"
                :style="{ background: getRiskColor(result[method].risk_level), border: 'none' }"
              >
                {{ result[method].risk_level }}风险
              </el-tag>
            </div>
          </template>
          <div class="method-body">
            <div class="method-reason">{{ result[method]?.reason }}</div>
            <div v-if="result[method]?.details" class="method-details">
              <div class="detail-section-title">详细数据</div>
              <div v-for="(val, key) in result[method].details" :key="key" class="detail-row">
                <span class="detail-key">{{ key }}</span>
                <span class="detail-val">{{ Array.isArray(val) ? val.join(', ') : val }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comparison { padding: 16px 24px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-family: var(--font-heading); font-size: 24px; font-weight: 600; color: #1E3A8A; margin: 0 0 8px 0; }
.subtitle { font-size: 14px; color: #64748B; margin: 0; }

.control-card { margin-bottom: 24px; border-radius: 10px; border: 1px solid #DBEAFE; }
.control-card :deep(.el-card__body) { padding: 16px 24px; }
.control-card :deep(.el-checkbox) { margin-right: 16px; }

.results-area { min-height: 120px; }
.results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 20px; }

.method-card { border-radius: 10px; border: 1px solid #DBEAFE; transition: all 0.25s ease; }
.method-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.method-highlight { border-color: #1E40AF; background: #f8fafc; }
.method-highlight :deep(.el-card__header) { background: #eff6ff; border-radius: 10px 12px 0 0; }

.method-header { display: flex; align-items: center; gap: 10px; }
.method-name { font-size: 16px; flex: 1; }

.method-body { display: flex; flex-direction: column; gap: 12px; }
.method-reason { font-size: 14px; color: #475569; line-height: 1.6; padding: 12px; background: #f8fafc; border-radius: 8px; }
.method-details { display: flex; flex-direction: column; gap: 6px; }
.detail-section-title { font-size: 12px; color: #64748B; font-weight: 600; margin-bottom: 4px; }
.detail-row { font-size: 13px; display: flex; gap: 8px; }
.detail-key { color: #64748B; min-width: 100px; }
.detail-val { color: #1E3A8A; font-weight: 500; }

/* ---- Skeleton Results ---- */
.sk-shimmer {
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 6px;
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.sk-result-card {
  background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 16px 24px;
  animation: sk-fade-in 0.25s ease-out both;
}
.sk-result-header { height: 20px; width: 180px; margin-bottom: 16px; }
.sk-result-body { height: 60px; margin-bottom: 12px; }
.sk-result-detail { height: 40px; width: 60%; }

@keyframes sk-fade-in {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
  .sk-shimmer { animation: none; background: #e2e8f0; }
  .sk-result-card { animation: none; opacity: 1; transform: none; }
}

@media (max-width: 1280px) {
  .comparison-page { padding: 14px 16px; }
}
@media (max-width: 1080px) {
  .comparison-page { padding: 12px 14px; }
}
</style>
