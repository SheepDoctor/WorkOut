<template>
  <div class="w-full max-w-lg h-full max-h-[800px] flex flex-col p-6 relative overflow-hidden"
       @touchstart="handleTouchStart"
       @touchend="handleTouchEnd">
      
      <!-- 加载状态 -->
      <div v-if="loading" class="absolute inset-0 z-50 bg-slate-950 flex flex-col items-center justify-center">
          <div class="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p class="text-slate-400">正在同步今日计划...</p>
      </div>

      <!-- 顶部进度指示 -->
      <header class="mb-6 flex items-center justify-between">
          <div class="flex gap-1.5">
              <div v-for="(_, i) in exercises" :key="i"
                   :class="['h-1 rounded-full transition-all duration-300', 
                            i === currentIndex ? 'w-8 bg-blue-500' : (i < currentIndex ? 'w-4 bg-emerald-500' : 'w-4 bg-slate-700')]">
              </div>
          </div>
          <span class="text-xs font-mono text-slate-500">
              动作 {{ currentIndex + 1 }} / {{ exercises.length }}
          </span>
      </header>

      <!-- 主内容区 -->
      <div class="flex-1 relative">
          <transition :name="transitionName">
              <div :key="currentIndex" class="w-full" v-if="exercises.length">
                  <div class="glass-card p-8 rounded-[2.5rem] shadow-2xl">
                      <div class="mb-8">
                          <span class="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-2 block">
                              {{ isCompleted ? '动作已完成' : '训练中' }}
                          </span>
                          <h1 class="text-4xl font-bold text-white mb-2 leading-tight">
                              {{ currentExercise.name }}
                          </h1>
                          <div class="flex items-center gap-2 text-slate-400">
                              <i class="fa-solid fa-hashtag text-xs"></i>
                              <span class="text-sm">第 {{ currentExercise.current }} 组 / 共 {{ currentExercise.total }} 组</span>
                          </div>
                      </div>

                      <!-- 环形进度 -->
                      <div class="relative w-48 h-48 mx-auto mb-10 flex items-center justify-center">
                          <svg class="w-full h-full transform -rotate-90">
                              <circle cx="96" cy="96" r="88" stroke="currentColor" stroke-width="8" fill="transparent" class="text-slate-800" />
                              <circle cx="96" cy="96" r="88" stroke="currentColor" stroke-width="12" fill="transparent" 
                                      :class="['progress-transition', isCompleted ? 'text-emerald-500' : 'text-blue-500']"
                                      :stroke-dasharray="2 * Math.PI * 88"
                                      :stroke-dashoffset="2 * Math.PI * 88 * (1 - currentPercent / 100)"
                                      stroke-linecap="round" />
                          </svg>
                          <div class="absolute inset-0 flex flex-col items-center justify-center">
                              <span class="text-4xl font-bold text-white">{{ isCompleted ? 'DONE' : currentPercent + '%' }}</span>
                              <button @click="incrementProgress" 
                                      class="mt-2 bg-white/10 hover:bg-white/20 px-3 py-1 rounded-full text-[10px] transition-colors text-white">
                                  +1 组
                              </button>
                          </div>
                      </div>

                      <!-- 动作要领 -->
                      <div class="bg-slate-900/40 rounded-3xl p-6 border border-white/5">
                          <div class="flex items-center gap-2 mb-4 text-xs font-bold text-slate-500 tracking-widest uppercase">
                              <i class="fa-solid fa-list-check text-blue-400"></i> 要领
                          </div>
                          <div class="space-y-3 max-h-32 overflow-y-auto pr-2">
                              <div v-for="(tip, tIndex) in parseTips(currentExercise.tips)" :key="tIndex" class="flex items-start gap-3">
                                  <div class="mt-2 w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                                  <p class="text-sm text-slate-300 leading-snug text-left">{{ tip }}</p>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>
          </transition>
      </div>

      <!-- 底部控制 -->
      <footer class="mt-8 flex items-center justify-between gap-4">
          <button @click="prev" :disabled="currentIndex === 0" class="w-14 h-14 rounded-2xl glass-card flex items-center justify-center disabled:opacity-20 transition-all text-white">
              <i class="fa-solid fa-chevron-left"></i>
          </button>
          
          <div class="flex-1 flex justify-center gap-4">
              <router-link to="/analyzer" class="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-slate-400 hover:text-white transition-colors" title="抖音分析">
                  <i class="fa-brands fa-tiktok"></i>
              </router-link>
              <router-link to="/pose" class="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-slate-400 hover:text-white transition-colors" title="动作指导">
                  <i class="fa-solid fa-camera"></i>
              </router-link>
              <router-link to="/muscle" class="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-slate-400 hover:text-white transition-colors" title="3D肌肉图">
                  <i class="fa-solid fa-child"></i>
              </router-link>
          </div>

          <button @click="next" :disabled="currentIndex === exercises.length - 1" class="w-14 h-14 rounded-2xl glass-card flex items-center justify-center disabled:opacity-20 transition-all text-white">
              <i class="fa-solid fa-chevron-right"></i>
          </button>
      </footer>

      <!-- 完成总结弹窗 -->
      <transition name="fade">
          <div v-if="showSummary" class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-xl flex items-center justify-center p-6 text-center text-white">
              <div>
                  <div class="text-6xl mb-6">🏆</div>
                  <h2 class="text-3xl font-bold mb-4">太棒了！</h2>
                  <p class="text-slate-400 mb-8">您已完成今日所有训练项目。</p>
                  <button @click="resetWorkout" class="px-8 py-4 bg-blue-600 rounded-2xl font-bold">重新开始</button>
              </div>
          </div>
      </transition>

      <!-- 配置模拟 -->
      <div class="mt-4 text-center">
          <span class="text-[9px] text-slate-700 uppercase tracking-widest">后端同步状态: {{ syncing ? '正在保存...' : '已就绪' }}</span>
      </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';

export default {
  name: 'HomeView',
  setup() {
    const exercises = ref([]);
    const currentIndex = ref(0);
    const loading = ref(true);
    const syncing = ref(false);
    const autoJumping = ref(false);
    const showSummary = ref(false);
    const transitionName = ref('slide-right');

    // --- 1. 后端交互函数 ---

    const fetchWorkout = async () => {
      loading.value = true;
      try {
        await new Promise(r => setTimeout(r, 1000));
        exercises.value = [
          { id: 101, name: "杠铃深蹲", current: 0, total: 5, tips: "核心收紧；膝盖对准脚尖；背挺直" },
          { id: 102, name: "哑铃卧推", current: 0, total: 4, tips: "沉肩收胛；双脚踩实；挺胸" },
          { id: 103, name: "引体向上", current: 0, total: 3, tips: "背阔肌发力；避免身体晃动" }
        ];
      } catch (e) {
        console.error("加载失败", e);
      } finally {
        loading.value = false;
      }
    };

    const syncProgress = async (exercise) => {
      syncing.value = true;
      try {
        console.log(`正在同步 ${exercise.name}: ${exercise.current}/${exercise.total}`);
        await new Promise(r => setTimeout(r, 300));
      } finally {
        syncing.value = false;
      }
    };

    // --- 2. 逻辑控制 ---

    const currentExercise = computed(() => exercises.value[currentIndex.value] || {});
    const currentPercent = computed(() => {
      if (!currentExercise.value.total) return 0;
      return Math.min(Math.round((currentExercise.value.current / currentExercise.value.total) * 100), 100);
    });
    const isCompleted = computed(() => currentExercise.value.current >= currentExercise.value.total);

    const incrementProgress = () => {
      if (isCompleted.value || autoJumping.value) return;
      currentExercise.value.current++;
      syncProgress(currentExercise.value);
      if (isCompleted.value) {
        handleAutoAdvance();
      }
    };

    const handleAutoAdvance = () => {
      if (currentIndex.value === exercises.value.length - 1) {
        setTimeout(() => showSummary.value = true, 800);
        return;
      }
      autoJumping.value = true;
      setTimeout(() => {
        if (autoJumping.value) {
          next();
          autoJumping.value = false;
        }
      }, 1500);
    };

    const next = () => {
      if (currentIndex.value < exercises.value.length - 1) {
        transitionName.value = 'slide-right';
        currentIndex.value++;
        autoJumping.value = false;
      }
    };

    const prev = () => {
      if (currentIndex.value > 0) {
        transitionName.value = 'slide-left';
        currentIndex.value--;
        autoJumping.value = false;
      }
    };

    const parseTips = (tips) => {
      if (!tips) return [];
      return Array.isArray(tips) ? tips : tips.split(/[；;。]/).filter(t => t.trim());
    };

    const resetWorkout = () => {
      exercises.value.forEach(e => e.current = 0);
      currentIndex.value = 0;
      showSummary.value = false;
    };

    // 手势监听
    let touchStartX = 0;
    const handleTouchStart = (e) => touchStartX = e.touches[0].clientX;
    const handleTouchEnd = (e) => {
      const deltaX = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(deltaX) > 80) deltaX > 0 ? prev() : next();
    };

    onMounted(fetchWorkout);

    return {
      exercises, currentIndex, currentExercise, currentPercent, isCompleted,
      loading, syncing, autoJumping, showSummary, transitionName,
      incrementProgress, next, prev, parseTips, resetWorkout,
      handleTouchStart, handleTouchEnd
    };
  }
}
</script>

<style scoped>
.glass-card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.slide-right-enter-active, .slide-right-leave-active,
.slide-left-enter-active, .slide-left-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: absolute; 
  width: 100%;
}
.slide-right-enter-from { transform: translateX(100%); opacity: 0; }
.slide-right-leave-to { transform: translateX(-100%); opacity: 0; }
.slide-left-enter-from { transform: translateX(-100%); opacity: 0; }
.slide-left-leave-to { transform: translateX(100%); opacity: 0; }

.progress-transition {
  transition: stroke-dashoffset 0.6s ease;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

