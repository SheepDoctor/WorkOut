<template>
  <transition name="celebration-fade">
    <div v-if="show" class="celebration-overlay fixed inset-0 z-[100] pointer-events-none">
      <!-- 背景光效 -->
      <div class="celebration-bg absolute inset-0"></div>
      
      <!-- 中央庆祝内容 -->
      <div class="celebration-content absolute inset-0 flex items-center justify-center">
        <div class="text-center celebration-main">
          <!-- 大图标 -->
          <div class="celebration-icon text-9xl mb-6">
            🎉
          </div>
          <!-- 文字 -->
          <h2 class="celebration-title text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-pink-300 to-cyan-300 mb-4">
            太棒了！
          </h2>
          <p class="text-2xl text-white font-bold mb-8">
            训练完成！
          </p>
        </div>
      </div>

      <!-- 粒子效果 -->
      <div class="particles absolute inset-0">
        <div v-for="i in 50" :key="i" 
             class="particle absolute"
             :style="getParticleStyle(i)">
        </div>
      </div>

      <!-- 彩带效果 -->
      <div class="confetti absolute inset-0">
        <div v-for="i in 30" :key="i" 
             class="confetti-piece absolute"
             :style="getConfettiStyle(i)">
        </div>
      </div>

      <!-- 烟花效果 -->
      <div class="fireworks absolute inset-0">
        <div v-for="i in 8" :key="i" 
             class="firework absolute"
             :style="getFireworkStyle(i)">
          <div v-for="j in 12" :key="j" 
               class="firework-particle absolute"
               :style="getFireworkParticleStyle(i, j)">
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'CelebrationAnimation',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    duration: {
      type: Number,
      default: 3000
    }
  },
  setup(props) {
    const particleStyles = ref([])
    const confettiStyles = ref([])
    const fireworkStyles = ref([])

    const getParticleStyle = (index) => {
      const angle = (Math.PI * 2 * index) / 50
      const velocity = 200 + Math.random() * 200
      const x = Math.cos(angle) * velocity
      const y = Math.sin(angle) * velocity
      const delay = Math.random() * 0.5
      const size = 4 + Math.random() * 6
      const colors = ['#fbbf24', '#f472b6', '#34d399', '#60a5fa', '#a78bfa', '#fb7185']
      const color = colors[Math.floor(Math.random() * colors.length)]

      return {
        left: '50%',
        top: '50%',
        width: `${size}px`,
        height: `${size}px`,
        backgroundColor: color,
        borderRadius: '50%',
        boxShadow: `0 0 ${size * 2}px ${color}`,
        animation: `particle-move-${index} 2s ease-out ${delay}s forwards`,
        '--x': `${x}px`,
        '--y': `${y}px`
      }
    }

    const getConfettiStyle = (index) => {
      const angle = (Math.PI * 2 * index) / 30
      const velocity = 300 + Math.random() * 200
      const x = Math.cos(angle) * velocity
      const y = Math.sin(angle) * velocity
      const delay = Math.random() * 0.3
      const rotation = Math.random() * 360
      const colors = ['#fbbf24', '#f472b6', '#34d399', '#60a5fa', '#a78bfa', '#fb7185', '#f59e0b']
      const color = colors[Math.floor(Math.random() * colors.length)]
      const width = 8 + Math.random() * 12
      const height = 8 + Math.random() * 12

      return {
        left: '50%',
        top: '50%',
        width: `${width}px`,
        height: `${height}px`,
        backgroundColor: color,
        animation: `confetti-move-${index} 2.5s ease-out ${delay}s forwards`,
        '--x': `${x}px`,
        '--y': `${y}px`,
        '--rotation': `${rotation + 720}deg`
      }
    }

    const getFireworkStyle = (index) => {
      const angle = (Math.PI * 2 * index) / 8
      const distance = 150 + Math.random() * 100
      const x = Math.cos(angle) * distance
      const y = Math.sin(angle) * distance
      const delay = 0.3 + index * 0.2

      return {
        left: `calc(50% + ${x}px)`,
        top: `calc(50% + ${y}px)`,
        animation: `firework-explode 1.5s ease-out ${delay}s forwards`
      }
    }

    const getFireworkParticleStyle = (fireworkIndex, particleIndex) => {
      const angle = (Math.PI * 2 * particleIndex) / 12
      const distance = 40 + Math.random() * 20
      const x = Math.cos(angle) * distance
      const y = Math.sin(angle) * distance
      const colors = ['#fbbf24', '#f472b6', '#34d399', '#60a5fa', '#a78bfa']
      const color = colors[Math.floor(Math.random() * colors.length)]
      const size = 3 + Math.random() * 4
      const delay = fireworkIndex * 0.2

      return {
        left: '50%',
        top: '50%',
        width: `${size}px`,
        height: `${size}px`,
        backgroundColor: color,
        borderRadius: '50%',
        animation: `firework-particle-${fireworkIndex}-${particleIndex} 1.5s ease-out ${delay}s forwards`,
        boxShadow: `0 0 ${size * 2}px ${color}`,
        '--x': `${x}px`,
        '--y': `${y}px`
      }
    }

    return {
      getParticleStyle,
      getConfettiStyle,
      getFireworkStyle,
      getFireworkParticleStyle
    }
  }
}
</script>

<style scoped>
.celebration-overlay {
  overflow: hidden;
}

.celebration-fade-enter-active {
  animation: celebration-fade-in 0.5s ease-out;
}

.celebration-fade-leave-active {
  animation: celebration-fade-out 0.5s ease-in;
}

@keyframes celebration-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes celebration-fade-out {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

.celebration-bg {
  background: radial-gradient(circle at center, 
    rgba(251, 191, 36, 0.3) 0%,
    rgba(244, 114, 182, 0.2) 30%,
    rgba(52, 211, 153, 0.2) 60%,
    rgba(96, 165, 250, 0.2) 90%,
    transparent 100%);
  animation: bg-pulse 2s ease-in-out infinite;
}

@keyframes bg-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.celebration-main {
  animation: main-enter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes main-enter {
  0% {
    opacity: 0;
    transform: scale(0.5) translateY(50px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.celebration-icon {
  filter: drop-shadow(0 0 20px rgba(251, 191, 36, 0.8));
  animation: icon-bounce 1s ease-in-out infinite;
}

@keyframes icon-bounce {
  0%, 100% { transform: translateY(0) scale(1) rotate(0deg); }
  25% { transform: translateY(-20px) scale(1.1) rotate(-5deg); }
  75% { transform: translateY(-10px) scale(1.05) rotate(5deg); }
}

.celebration-title {
  text-shadow: 0 0 30px rgba(251, 191, 36, 0.8),
               0 0 60px rgba(244, 114, 182, 0.6);
  animation: title-glow 2s ease-in-out infinite;
}

@keyframes title-glow {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.5); }
}

/* 粒子动画 - 使用动态生成 */
.particle {
  animation: particle-move-base 2s ease-out forwards;
}

@keyframes particle-move-base {
  0% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(var(--x, 0), var(--y, 0)) scale(0);
  }
}

/* 彩带动画 */
.confetti-piece {
  animation: confetti-move-base 2.5s ease-out forwards;
}

@keyframes confetti-move-base {
  0% {
    opacity: 1;
    transform: translate(0, 0) rotate(0deg);
  }
  100% {
    opacity: 0;
    transform: translate(var(--x, 0), var(--y, 0)) rotate(var(--rotation, 720deg));
  }
}

/* 烟花动画 */
@keyframes firework-explode {
  0% {
    opacity: 1;
    transform: scale(0);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(1);
  }
}

.firework {
  animation: firework-explode 1.5s ease-out forwards;
}

.firework-particle {
  animation: firework-particle-base 1.5s ease-out forwards;
}

@keyframes firework-particle-base {
  0% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(var(--x, 0), var(--y, 0)) scale(0);
  }
}
</style>

