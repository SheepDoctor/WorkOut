import { createRouter, createWebHistory } from 'vue-router'
import DouyinAnalyzer from '../views/DouyinAnalyzer.vue'
import PoseAnalyzer from '../views/PoseAnalyzer.vue'
import Muscle3DViewer from '../views/Muscle3DViewer.vue'

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
  },
  {
    path: '/muscle',
    name: 'Muscle3DViewer',
    component: Muscle3DViewer
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

