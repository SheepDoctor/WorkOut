<template>
  <div id="app">
    <nav v-if="!isMusclePage" class="navbar">
      <div class="container">
        <h1 class="logo">💪 WorkOut</h1>
        <div class="nav-links">
          <router-link to="/" class="nav-link">抖音分析</router-link>
          <router-link to="/pose" class="nav-link">动作指导</router-link>
          <router-link to="/muscle" class="nav-link">3D肌肉图</router-link>
        </div>
      </div>
    </nav>
    <main :class="['main-content', { 'fullscreen': isMusclePage }]">
      <router-view />
    </main>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const isMusclePage = computed(() => route.path === '/muscle')
    
    return {
      isMusclePage
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  color: #667eea;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: #f0f0f0;
  color: #667eea;
}

.nav-link.router-link-active {
  background: #667eea;
  color: white;
}

.main-content {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.main-content.fullscreen {
  max-width: 100%;
  margin: 0;
  padding: 0;
}
</style>

