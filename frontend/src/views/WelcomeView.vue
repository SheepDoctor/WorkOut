<template>
  <div class="welcome-container w-full h-full flex flex-col items-center justify-center relative overflow-hidden bg-black" @click="enterApp">
    
    <!-- 1. 深空背景层 -->
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-950/50 via-slate-950 to-black z-0"></div>
    
    <!-- 2. 动态极光/星云效果 -->
    <div class="absolute inset-0 opacity-40 mix-blend-screen overflow-hidden pointer-events-none">
      <div class="absolute -top-[20%] -left-[10%] w-[70%] h-[70%] bg-blue-600/30 rounded-full blur-[120px] animate-blob"></div>
      <div class="absolute top-[20%] -right-[10%] w-[60%] h-[60%] bg-purple-600/30 rounded-full blur-[120px] animate-blob [animation-delay:2s]"></div>
      <div class="absolute -bottom-[20%] left-[20%] w-[60%] h-[60%] bg-cyan-600/30 rounded-full blur-[120px] animate-blob [animation-delay:4s]"></div>
    </div>

    <!-- 3. 网格装饰 (增加科技感) -->
    <div class="absolute inset-0 bg-[url('/grid.svg')] opacity-10 mix-blend-overlay z-0 scale-150 animate-pulse-slow"></div>

    <!-- 主内容区 -->
    <div class="relative z-10 flex flex-col items-center w-full max-w-4xl px-6">
      
      <!-- Logo 容器：核心视觉 -->
      <div class="relative w-full flex justify-center mb-16 group cursor-pointer" @click="enterApp">
        <!-- 背后辉光 (强力渲染) -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-gradient-to-r from-cyan-500/20 via-blue-500/20 to-purple-500/20 rounded-full blur-3xl opacity-50 group-hover:opacity-80 transition-opacity duration-1000 animate-pulse-slow"></div>
        
        <!-- 标题图片 (应用遮罩和混合) -->
        <div class="relative z-10 image-wrapper transition-transform duration-700 group-hover:scale-105">
           <!-- 
              mask-image: 使用径向渐变让边缘透明，消除硬边框
              mix-blend-mode: screen 如果图片是黑底白字，可以完美去底；如果是透明底，screen也能增加发光感
           -->
          <img 
            src="/title.png" 
            alt="GYMX AI Fitness Coach" 
            class="w-full h-auto object-contain max-h-[40vh] drop-shadow-[0_0_15px_rgba(100,200,255,0.3)] mask-radial-faded" 
          />
          
          <!-- 图片表面的扫光效果 -->
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-shimmer skew-x-12"></div>
        </div>
      </div>

      <!-- 交互提示 -->
      <div class="text-center space-y-6 animate-fade-in-up delay-300">
        <div class="relative inline-block group">
          <p class="text-cyan-200/80 text-sm sm:text-base font-light tracking-[0.5em] uppercase animate-pulse group-hover:text-white transition-colors duration-300">
            Press any key to start
          </p>
          <!-- 下划线光效 -->
          <div class="absolute -bottom-2 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50 group-hover:opacity-100 group-hover:w-full transition-all duration-500"></div>
        </div>
        
        <p class="text-slate-500 text-[10px] sm:text-xs tracking-[0.3em] uppercase opacity-40 transform translate-y-2">
          Touch Screen / Press Key
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'WelcomeView',
  setup() {
    const router = useRouter();

    const enterApp = () => {
      // 添加离场动画逻辑（可选，目前直接跳转）
      router.push('/home');
    };

    const handleKeydown = (e) => {
      enterApp();
    };

    onMounted(() => {
      window.addEventListener('keydown', handleKeydown);
      window.addEventListener('touchstart', enterApp);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('keydown', handleKeydown);
      window.removeEventListener('touchstart', enterApp);
    });

    return {
      enterApp
    };
  }
}
</script>

<style scoped>
.welcome-container {
  min-height: 100vh;
  cursor: pointer;
  /* 禁止文本选择，提升沉浸感 */
  user-select: none; 
}

/* 核心技巧：图片边缘羽化遮罩 */
.mask-radial-faded {
  /* 从中心向外：不透明 -> 透明 */
  -webkit-mask-image: radial-gradient(ellipse at center, black 60%, transparent 100%);
  mask-image: radial-gradient(ellipse at center, black 60%, transparent 100%);
}

.animate-fade-in-up {
  animation: fadeInUp 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 背景光斑浮动动画 */
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.animate-blob {
  animation: blob 10s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.3; }
}

.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.group-hover\:animate-shimmer {
  animation: shimmer 1.5s infinite;
}
</style>
