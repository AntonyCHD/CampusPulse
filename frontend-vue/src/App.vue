<script setup lang="ts">
import { computed, ref } from "vue"
import { useRouter, useRoute, RouterView } from "vue-router"
import {
  DataBoard, TrendCharts, DataAnalysis, Connection, Files, Setting, Tools,
  Cpu, Warning
} from "@element-plus/icons-vue"

const router = useRouter()
const route = useRoute()

interface DockItem {
  path: string
  label: string
  icon: any
}

const dockItems: DockItem[] = [
  { path: "/",           label: "事件总览", icon: DataBoard },
  { path: "/comparison", label: "方法对比", icon: DataAnalysis },
  { path: "/graph",      label: "评论图谱", icon: Connection },
  { path: "/intervention", label: "证据处置", icon: Setting },
  { path: "/report",     label: "报告导出", icon: Files },
  { path: "/settings",   label: "系统配置", icon: Tools },
]

const isActive = (path: string): boolean => {
  if (path === "/") return route.path === "/"
  return route.path.startsWith(path)
}

const navigate = (item: DockItem) => {
  router.push(item.path)
}

const dockCollapsed = ref(false)

const toggleDock = () => {
  dockCollapsed.value = !dockCollapsed.value
}

const currentLabel = computed(() => {
  const item = dockItems.find(d => isActive(d.path))
  return item?.label ?? "群声雷达"
})
</script>

<template>
  <div id="app">
    <header class="top-bar">
      <div class="top-bar-left" @click="router.push('/')" style="cursor:pointer">
        <svg width="24" height="24" viewBox="0 0 36 36" fill="none" class="top-brand-icon">
          <circle cx="18" cy="18" r="16" stroke="currentColor" stroke-width="2" opacity="0.6"/>
          <circle cx="18" cy="18" r="6" fill="currentColor" opacity="0.9"/>
          <path d="M18 2 A16 16 0 0 1 30 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
          <path d="M18 2 A16 16 0 0 0 10 26" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.3"/>
          <line x1="18" y1="6" x2="18" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span class="top-brand-name">群声雷达</span>
        <span class="top-brand-divider">/</span>
        <span class="top-brand-section">{{ currentLabel }}</span>
      </div>
      <div class="top-bar-right">
        <span class="system-status"><span class="status-dot-live"></span> 系统运行中</span>
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>

    <nav class="dock">
      <div class="dock-inner">
        <button
          v-for="item in dockItems"
          :key="item.path"
          class="dock-item"
          :class="{ active: isActive(item.path) }"
          @click="navigate(item)"
          :title="item.label"
        >
          <component :is="item.icon" class="dock-icon" />
          <span class="dock-label">{{ item.label }}</span>
        </button>
      </div>
    </nav>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --color-primary: #1E40AF;
  --color-primary-light: #3B82F6;
  --color-accent: #D97706;
  --color-bg: #F8FAFC;
  --color-surface: #FFFFFF;
  --color-text: #1E3A8A;
  --color-text-secondary: #64748B;
  --color-border: #DBEAFE;
  --color-muted: #E9EEF6;
  --color-danger: #DC2626;
  --topbar-height: 44px;
  --dock-height: 60px;
  --font-heading: 'Fira Code', monospace;
  --font-body: 'Fira Sans', system-ui, sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-bg);
}

.top-bar {
  position: fixed; top: 0; left: 0; right: 0;
  height: var(--topbar-height);
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  border-bottom: 1px solid rgba(30,64,175,0.08);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; z-index: 200;
}

.top-bar-left { display: flex; align-items: center; gap: 8px; min-width: 0; }
.top-brand-icon { color: var(--color-primary); flex-shrink: 0; }

.top-brand-name {
  font-family: var(--font-heading); font-size: 15px; font-weight: 600;
  color: var(--color-primary); letter-spacing: 0.5px; white-space: nowrap;
}

.top-brand-divider { color: #cbd5e1; font-size: 14px; margin: 0 2px; }

.top-brand-section {
  font-size: 13px; font-weight: 500;
  color: var(--color-text-secondary); white-space: nowrap;
}

.top-bar-right { display: flex; align-items: center; gap: 12px; }

.system-status {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; color: var(--color-text-secondary);
}

.status-dot-live {
  width: 7px; height: 7px; border-radius: 50%; background: #10b981;
  box-shadow: 0 0 5px rgba(16,185,129,0.4);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.5} }

.main-content {
  margin-top: var(--topbar-height);
  margin-bottom: calc(var(--dock-height) + 4px);
  flex: 1; overflow-x: hidden; min-height: 0;
}

.dock {
  position: fixed; bottom: 12px; left: 50%;
  transform: translateX(-50%); z-index: 200;
}

.dock-inner {
  display: flex; gap: 4px;
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(30,64,175,0.1);
  border-radius: 16px; padding: 6px;
  box-shadow: 0 4px 24px rgba(30,64,175,0.06), 0 1px 3px rgba(0,0,0,0.04);
}

.dock-item {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 8px 16px; border: none; border-radius: 12px;
  background: transparent; color: var(--color-text-secondary);
  font-family: var(--font-body); font-size: 10px; font-weight: 500;
  cursor: pointer; transition: all 0.2s ease;
  min-width: 60px; text-align: center;
}

.dock-item:hover { background: rgba(30,64,175,0.06); color: var(--color-primary); }
.dock-item.active { background: rgba(30,64,175,0.1); color: var(--color-primary); font-weight: 600; }

.dock-icon { width: 22px; height: 22px; flex-shrink: 0; }
.dock-label { white-space: nowrap; letter-spacing: 0.2px; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(30,64,175,0.12); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(30,64,175,0.22); }

/* Collapsed dock */
.dock.collapsed .dock-inner {
  gap: 2px;
}

.dock.collapsed .dock-item {
  min-width: 44px;
  padding: 8px 10px;
}

.dock.collapsed .dock-label {
  display: none;
}

.dock-divider {
  width: 1px;
  height: 24px;
  background: rgba(30, 64, 175, 0.12);
  border-radius: 1px;
  align-self: center;
  margin: 0 4px;
}

.dock-collapse-icon {
  transition: transform 0.25s ease;
}

.dock-collapse-icon.flipped {
  transform: rotate(180deg);
}

</style>