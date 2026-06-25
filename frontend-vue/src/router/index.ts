import { createRouter, createWebHistory } from 'vue-router'
import EventList from '../views/EventList.vue'
import EventAnalysis from '../views/EventAnalysis.vue'
import CommentGraph from '../views/CommentGraph.vue'
import Comparison from '../views/Comparison.vue'
import ReportExport from '../views/ReportExport.vue'
import Intervention from '../views/Intervention.vue'
import Settings from '../views/Settings.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'event-list', component: EventList },
    { path: '/event/:id', name: 'event-analysis', component: EventAnalysis },
    { path: '/comparison', name: 'comparison', component: Comparison },
    { path: '/graph', name: 'comment-graph', component: CommentGraph },
    { path: '/graph/:id', name: 'comment-graph-event', component: CommentGraph },
    { path: '/intervention', name: 'intervention', component: Intervention },
    { path: '/intervention/:id', name: 'intervention-event', component: Intervention },
    { path: '/report', name: 'report-export', component: ReportExport },
    { path: '/report/:id', name: 'report-export-event', component: ReportExport },
    { path: '/settings', name: 'settings', component: Settings },
  ]
})

export default router
