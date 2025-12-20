<template>
  <div id="app" class="h-screen flex items-center justify-center gradient-bg">
    <main class="w-full h-full flex items-center justify-center">
      <transition :name="transitionName" mode="out-in">
        <router-view :key="$route.path" />
      </transition>
    </main>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const transitionName = ref('fade')

    watch(() => route.path, (to, from) => {
      // 根据路由变化方向决定过渡动画
      const routes = ['/', '/analyzer', '/muscle', '/achievements']
      const toIndex = routes.indexOf(to)
      const fromIndex = routes.indexOf(from)
      
      if (toIndex > fromIndex) {
        transitionName.value = 'slide-left'
      } else if (toIndex < fromIndex) {
        transitionName.value = 'slide-right'
      } else {
        transitionName.value = 'fade'
      }
    })

    return {
      transitionName
    }
  }
}
</script>

<script>
export default {
  name: 'App'
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  margin: 0;
  padding: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
  color: #f8fafc;
  overflow: hidden;
}

#app {
  width: 100vw;
  height: 100vh;
}

.gradient-bg {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
  position: relative;
}

.gradient-bg::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(168, 85, 247, 0.15) 0%, transparent 50%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.fade-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-100px);
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-100px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>

