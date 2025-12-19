import { createRouter, createWebHistory } from 'vue-router'
import DouyinAnalyzer from '../views/DouyinAnalyzer.vue'
import PoseAnalyzer from '../views/PoseAnalyzer.vue'

const routes = [
  {
    path: '/',
    name: 'DouyinAnalyzer',
    component: DouyinAnalyzer
  },
  {
    path: '/pose',
    name: 'PoseAnalyzer',
    component: PoseAnalyzer
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

