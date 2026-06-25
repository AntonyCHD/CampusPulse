<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from "vue"
import { useRouter } from "vue-router"
import { api, type Event, type DashboardSummary } from "../api/client"
import { Search, Warning, TrendCharts } from "@element-plus/icons-vue"
import * as echarts from "echarts"

const router = useRouter()
const events = ref<Event[]>([])
const summary = ref<DashboardSummary | null>(null)
const loading = ref(false)
const riskFilter = ref("")
const typeFilter = ref("")

let riskDistChart: echarts.ECharts | null = null
let typeDistChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

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
  } catch (error) {
    console.error("Failed to load events:", error)
  } finally {
    loading.value = false
  }
}