import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DouyinAnalyzer from '../views/DouyinAnalyzer.vue'
import Muscle3DViewer from '../views/Muscle3DViewer.vue'
import AchievementsView from '../views/AchievementsView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/analyzer',
    name: 'DouyinAnalyzer',
    component: DouyinAnalyzer
  },
  {
    path: '/muscle',
    name: 'Muscle3DViewer',
    component: Muscle3DViewer
  },
  {
    path: '/achievements',
    name: 'Achievements',
    component: AchievementsView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

