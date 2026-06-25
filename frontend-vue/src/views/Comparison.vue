<script setup lang="ts">
import { ref, computed } from "vue"
import { api } from "../api/client"

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

    <div v-loading="loading" class="results-area">
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
.comparison { max-width: 1400px; padding: 20px 24px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-family: var(--font-heading); font-size: 24px; font-weight: 600; color: #1E3A8A; margin: 0 0 8px 0; }
.subtitle { font-size: 14px; color: #64748B; margin: 0; }

.control-card { margin-bottom: 24px; border-radius: 10px; border: 1px solid #DBEAFE; }
.control-card :deep(.el-card__body) { padding: 24px; }
.control-card :deep(.el-checkbox) { margin-right: 16px; }

.results-area { min-height: 300px; }
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
</style>
