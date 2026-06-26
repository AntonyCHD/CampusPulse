<script setup lang="ts">
defineProps<{ section: string }>()
</script>

<template>
  <!-- Metrics Row -->
  <div v-if="section === 'metrics'" class="sk-metrics">
    <div v-for="i in 4" :key="i" class="sk-metric-card" :style="{ animationDelay: i * 40 + 'ms' }">
      <div class="sk-shimmer sk-metric-icon"></div>
      <div class="sk-metric-text">
        <div class="sk-shimmer sk-line-sm"></div>
        <div class="sk-shimmer sk-line-md"></div>
      </div>
    </div>
  </div>

  <!-- Marquee Bar -->
  <div v-if="section === 'marquee'" class="sk-marquee">
    <div class="sk-shimmer sk-marquee-label"></div>
    <div class="sk-shimmer sk-marquee-track"></div>
  </div>

  <!-- Chart -->
  <div v-if="section === 'chart'" class="sk-chart">
    <div class="sk-shimmer sk-chart-header"></div>
    <div class="sk-shimmer sk-chart-body"></div>
  </div>

  <!-- Table -->
  <div v-if="section === 'table'" class="sk-table">
    <div class="sk-shimmer sk-table-header"></div>
    <div v-for="i in 5" :key="i" class="sk-table-row" :style="{ animationDelay: i * 40 + 'ms' }">
      <div class="sk-shimmer sk-table-cell" style="width:8%"></div>
      <div class="sk-shimmer sk-table-cell" style="width:35%"></div>
      <div class="sk-shimmer sk-table-cell" style="width:12%"></div>
      <div class="sk-shimmer sk-table-cell" style="width:15%"></div>
      <div class="sk-shimmer sk-table-cell" style="width:15%"></div>
      <div class="sk-shimmer sk-table-cell" style="width:10%"></div>
    </div>
  </div>

  <!-- Card List -->
  <div v-if="section === 'cards'" class="sk-cards">
    <div v-for="i in 6" :key="i" class="sk-card-row" :style="{ animationDelay: i * 40 + 'ms' }">
      <div class="sk-shimmer sk-card-dot"></div>
      <div class="sk-card-content">
        <div class="sk-shimmer sk-line-lg"></div>
        <div class="sk-shimmer sk-line-sm"></div>
      </div>
      <div class="sk-card-right">
        <div class="sk-shimmer sk-tag"></div>
        <div class="sk-shimmer sk-line-xs"></div>
      </div>
    </div>
  </div>

  <!-- Section -->
  <div v-if="section === 'section'" class="sk-section">
    <div class="sk-shimmer sk-section-header"></div>
    <div class="sk-shimmer sk-section-body"></div>
  </div>

  <!-- Two Column -->
  <div v-if="section === 'two-col'" class="sk-two-col">
    <div class="sk-col-left">
      <div class="sk-shimmer sk-col-header"></div>
      <div v-for="i in 4" :key="i" class="sk-shimmer sk-col-row" :style="{ animationDelay: i * 40 + 'ms' }"></div>
    </div>
    <div class="sk-col-right">
      <div class="sk-shimmer sk-col-header"></div>
      <div v-for="i in 3" :key="i" class="sk-shimmer sk-col-card" :style="{ animationDelay: i * 40 + 'ms' }"></div>
    </div>
  </div>

  <!-- Intervention skeleton -->
  <div v-if="section === 'intervention'" class="sk-intervention">
    <div class="sk-shimmer sk-info-bar"></div>
    <div class="sk-shimmer sk-workflow"></div>
    <div class="sk-intervention-grid">
      <div class="sk-int-left">
        <div v-for="i in 3" :key="i" class="sk-shimmer sk-int-card" :style="{ animationDelay: i * 50 + 'ms' }"></div>
      </div>
      <div class="sk-int-right">
        <div v-for="i in 3" :key="i" class="sk-shimmer sk-int-card-sm" :style="{ animationDelay: i * 50 + 'ms' }"></div>
      </div>
    </div>
  </div>

  <!-- Report skeleton -->
  <div v-if="section === 'report'" class="sk-report">
    <div v-for="i in 4" :key="i" class="sk-report-section" :style="{ animationDelay: i * 60 + 'ms' }">
      <div class="sk-shimmer sk-report-header"></div>
      <div class="sk-shimmer sk-report-body"></div>
    </div>
  </div>

  <!-- Graph skeleton -->
  <div v-if="section === 'graph'" class="sk-graph">
    <div class="sk-shimmer sk-graph-body"></div>
    <div class="sk-graph-stats">
      <div v-for="i in 5" :key="i" class="sk-shimmer sk-stat-box" :style="{ animationDelay: i * 40 + 'ms' }"></div>
    </div>
  </div>

  <!-- Post Card skeleton -->
  <div v-if="section === 'post-card'" class="sk-section" style="margin-bottom:20px">
    <div class="sk-shimmer sk-section-header" style="width:180px"></div>
    <div class="sk-shimmer" style="height:20px;width:60%;margin-bottom:10px"></div>
    <div class="sk-shimmer sk-section-body"></div>
  </div>

  <!-- Evolution steps skeleton -->
  <div v-if="section === 'steps'" class="sk-section">
    <div class="sk-shimmer sk-section-header"></div>
    <div class="sk-shimmer" style="height:60px"></div>
  </div>
</template>

<style scoped>
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

.sk-metric-card,
.sk-table-row,
.sk-card-row,
.sk-col-row,
.sk-col-card,
.sk-int-card,
.sk-int-card-sm,
.sk-report-section,
.sk-stat-box {
  animation: sk-fade-in 0.25s ease-out both;
}

@keyframes sk-fade-in {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
  .sk-shimmer { animation: none; background: #e2e8f0; }
  .sk-metric-card, .sk-table-row, .sk-card-row,
  .sk-col-row, .sk-col-card, .sk-int-card,
  .sk-int-card-sm, .sk-report-section, .sk-stat-box {
    animation: none; opacity: 1; transform: none;
  }
}

/* Metrics */
.sk-metrics { display: flex; gap: 24px; margin-bottom: 16px; }
.sk-metric-card { display: flex; align-items: center; gap: 12px; flex: 1; background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 16px 18px; }
.sk-metric-icon { width: 40px; height: 40px; border-radius: 8px; flex-shrink: 0; }
.sk-metric-text { display: flex; flex-direction: column; gap: 6px; flex: 1; }
.sk-line-sm { height: 12px; width: 60%; }
.sk-line-md { height: 18px; width: 40%; }
.sk-line-lg { height: 16px; width: 80%; }
.sk-line-xs { height: 10px; width: 50px; }

/* Marquee */
.sk-marquee { display: flex; align-items: center; height: 52px; margin-bottom: 20px; background: white; border: 1px solid #DBEAFE; border-radius: 10px; overflow: hidden; padding: 0 16px; gap: 16px; }
.sk-marquee-label { width: 90px; height: 28px; flex-shrink: 0; }
.sk-marquee-track { flex: 1; height: 24px; }

/* Chart */
.sk-chart { background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; }
.sk-chart-header { height: 16px; width: 80px; margin-bottom: 12px; }
.sk-chart-body { height: 280px; }

/* Table */
.sk-table { background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 14px 18px; }
.sk-table-header { height: 14px; width: 120px; margin-bottom: 14px; }
.sk-table-row { display: flex; gap: 8px; margin-bottom: 10px; }
.sk-table-cell { height: 14px; border-radius: 4px; }

/* Card List */
.sk-cards { background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 12px 20px; }
.sk-card-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f8fafc; }
.sk-card-row:last-child { border-bottom: none; }
.sk-card-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.sk-card-content { display: flex; flex-direction: column; gap: 6px; flex: 1; }
.sk-card-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.sk-tag { width: 36px; height: 22px; border-radius: 4px; }

/* Section */
.sk-section { background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px; }
.sk-section-header { height: 16px; width: 130px; margin-bottom: 14px; }
.sk-section-body { height: 120px; }

/* Two Column */
.sk-two-col { display: grid; grid-template-columns: 1fr 360px; gap: 20px; }
.sk-col-left { background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 14px 18px; }
.sk-col-right { background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 14px 18px; display: flex; flex-direction: column; gap: 10px; }
.sk-col-header { height: 14px; width: 80px; margin-bottom: 12px; }
.sk-col-row { height: 36px; margin-bottom: 8px; border-radius: 6px; }
.sk-col-card { height: 80px; border-radius: 8px; }

/* Intervention */
.sk-intervention { display: flex; flex-direction: column; gap: 16px; }
.sk-info-bar { height: 52px; border-radius: 10px; }
.sk-workflow { height: 80px; border-radius: 10px; }
.sk-intervention-grid { display: grid; grid-template-columns: 1fr 420px; gap: 20px; }
.sk-int-left { display: flex; flex-direction: column; gap: 16px; }
.sk-int-card { height: 180px; border-radius: 10px; }
.sk-int-right { display: flex; flex-direction: column; gap: 16px; }
.sk-int-card-sm { height: 140px; border-radius: 10px; }

/* Report */
.sk-report { display: flex; flex-direction: column; gap: 16px; }
.sk-report-section { background: white; border: 1px solid #DBEAFE; border-radius: 10px; padding: 16px 20px; }
.sk-report-header { height: 16px; width: 100px; margin-bottom: 14px; }
.sk-report-body { height: 100px; }

/* Graph */
.sk-graph { display: flex; flex-direction: column; gap: 16px; }
.sk-graph-body { height: 420px; border-radius: 10px; }
.sk-graph-stats { display: flex; gap: 16px; }
.sk-stat-box { flex: 1; height: 70px; border-radius: 10px; }

@media (max-width: 1280px) {
  .sk-two-col,
  .sk-intervention-grid { grid-template-columns: 1fr; }
  .sk-metrics { gap: 12px; flex-wrap: wrap; }
  .sk-metric-card { flex: 1 1 220px; }
}

@media (max-width: 1080px) {
  .sk-chart-body { height: 220px; }
  .sk-graph-body { height: 320px; }
  .sk-graph-stats { flex-wrap: wrap; }
  .sk-stat-box { flex: 1 1 140px; }
  .sk-card-right { display: none; }
}

</style>
