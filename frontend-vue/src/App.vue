<script setup lang="ts">
import { computed, ref } from "vue"
import { useRouter, useRoute, RouterView } from "vue-router"
import {
  DataBoard, TrendCharts, DataAnalysis, Connection, Files, Setting, Tools
} from "@element-plus/icons-vue"

const router = useRouter()
const route = useRoute()
const sidebarCollapsed = ref(false)

interface NavGroup {
  label: string
  items: NavItem[]
}

interface NavItem {
  path: string
  label: string
  icon: any
}

const navGroups: NavGroup[] = [
  {
    label: "监测",
    items: [
      { path: "/", label: "事件总览", icon: DataBoard },
      { path: "/comparison", label: "方法对比", icon: DataAnalysis },
    ]
  },
  {
    label: "分析",
    items: [
      { path: "/graph", label: "评论图谱", icon: Connection },
      { path: "/intervention", label: "证据处置", icon: Setting },
      { path: "/report", label: "报告导出", icon: Files },
    ]
  },
  {
    label: "系统",
    items: [
      { path: "/settings", label: "系统配置", icon: Tools },
    ]
  }
]

const isActive = (path: string): boolean => {
  if (path === "/") return route.path === "/"
  return route.path.startsWith(path)
}

const navigate = (item: NavItem) => {
  router.push(item.path)
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<template>
  <div id="app">
    <!-- Right Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-brand" @click="router.push('/')" style="cursor: pointer">
        <div class="brand-icon">
          <svg width="32" height="32" viewBox="0 0 36 36" fill="none">
            <circle cx="18" cy="18" r="16" stroke="currentColor" stroke-width="2" opacity="0.6"/>
            <circle cx="18" cy="18" r="6" fill="currentColor" opacity="0.9"/>
            <path d="M18 2 A16 16 0 0 1 30 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
            <path d="M18 2 A16 16 0 0 0 10 26" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.3"/>
            <line x1="18" y1="6" x2="18" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="brand-text" v-show="!sidebarCollapsed">
          <span class="brand-name">群声雷达</span>
          <span class="brand-sub">Campus Opinion Radar</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <template v-for="group in navGroups" :key="group.label">
          <div class="nav-group-label" v-show="!sidebarCollapsed">{{ group.label }}</div>
          <button
            v-for="item in group.items"
            :key="item.path"
            class="nav-item"
            :class="{ active: isActive(item.path) }"
            @click="navigate(item)"
            :title="sidebarCollapsed ? item.label : ''"
          >
            <component :is="item.icon" class="nav-icon" />
            <span class="nav-label" v-show="!sidebarCollapsed">{{ item.label }}</span>
          </button>
        </template>
      </nav>

      <div class="sidebar-footer">
        <button class="collapse-btn" @click="toggleSidebar" :title="sidebarCollapsed ? '展开' : '折叠'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline v-if="sidebarCollapsed" points="13 7 18 12 13 17" />
            <polyline v-else points="11 7 6 12 11 17" />
          </svg>
        </button>
        <div class="status-indicator" v-show="!sidebarCollapsed">
          <span class="status-dot"></span>
          <span class="status-text">系统运行中</span>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
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
  --color-danger: #DC2626;
  --sidebar-width: 220px;
  --sidebar-collapsed-width: 56px;
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
  min-height: 100vh;
  background: var(--color-bg);
}

/* ===== Right Sidebar ===== */
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  border-right: 1px solid rgba(30, 64, 175, 0.08);
  display: flex;
  flex-direction: column;
  z-index: 100;
  padding: 20px 0 16px;
  transition: width 0.25s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px 16px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 8px;
}

.sidebar.collapsed .sidebar-brand {
  padding: 0 12px 16px;
  justify-content: center;
}

.brand-icon { color: var(--color-primary); flex-shrink: 0; }

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  white-space: nowrap;
}

.brand-name {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: 0.5px;
}

.brand-sub {
  font-size: 10px;
  font-weight: 400;
  color: var(--color-text-secondary);
  letter-spacing: 0.3px;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 8px 8px;
  overflow-y: auto;
}

.nav-group-label {
  font-size: 10px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 12px 12px 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--color-text-secondary);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 10px 0;
}

.nav-item:hover {
  background: rgba(30, 64, 175, 0.06);
  color: var(--color-primary);
}

.nav-item.active {
  background: rgba(30, 64, 175, 0.1);
  color: var(--color-primary);
  font-weight: 600;
}

.nav-icon { width: 20px; height: 20px; flex-shrink: 0; }
.nav-label { white-space: nowrap; }

/* Sidebar Footer */
.sidebar-footer {
  padding: 12px 16px 0;
  border-top: 1px solid var(--color-border);
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar.collapsed .sidebar-footer {
  flex-direction: column;
  gap: 12px;
  padding: 12px 0 0;
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: white;
  color: var(--color-text-secondary);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.collapse-btn:hover {
  background: rgba(30, 64, 175, 0.06);
  color: var(--color-primary);
  border-color: rgba(30, 64, 175, 0.2);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 5px rgba(16, 185, 129, 0.4);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text { font-size: 11px; color: var(--color-text-secondary); white-space: nowrap; }

/* Main Content */
.main-content {
  margin-left: var(--sidebar-width);
  flex: 1;
  min-height: 100vh;
  max-width: 1600px;
  margin-right: auto;
  overflow-x: hidden;
  transition: margin-left 0.25s ease;
}

.sidebar.collapsed ~ .main-content {
  margin-left: var(--sidebar-collapsed-width);
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(30, 64, 175, 0.12); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(30, 64, 175, 0.22); }
</style>