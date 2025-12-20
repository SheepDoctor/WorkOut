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
          <div class="flex gap-4 items-center">
              <button @click="showHistory = true" class="text-slate-400 hover:text-white transition-colors">
                  <i class="fa-solid fa-clock-rotate-left"></i>
              </button>
              <div class="flex gap-1.5">
                  <div v-for="(_, i) in exercises" :key="i"
                       :class="['h-1 rounded-full transition-all duration-300', 
                                i === currentIndex ? 'w-8 bg-blue-500' : (i < currentIndex ? 'w-4 bg-emerald-500' : 'w-4 bg-slate-700')]">
                  </div>
              </div>
          </div>
          <span class="text-xs font-mono text-slate-500">
              动作 {{ currentIndex + 1 }} / {{ exercises.length }}
          </span>
      </header>

      <!-- 历史记录侧边栏 -->
      <transition name="slide-fade">
          <div v-if="showHistory" class="fixed inset-0 z-[60] bg-slate-950/80 backdrop-blur-md">
              <div class="absolute right-0 top-0 bottom-0 w-80 bg-slate-900 shadow-2xl p-6 overflow-y-auto">
                  <div class="flex items-center justify-between mb-8">
                      <h2 class="text-xl font-bold text-white">训练历史</h2>
                      <button @click="showHistory = false" class="text-slate-400 hover:text-white">
                          <i class="fa-solid fa-xmark"></i>
                      </button>
                  </div>

                  <div v-if="history.length === 0" class="text-center py-20 text-slate-500">
                      <i class="fa-solid fa-ghost text-4xl mb-4 opacity-20"></i>
                      <p>暂无历史记录</p>
                  </div>

                  <div class="space-y-4">
                      <div v-for="item in history" :key="item.id" 
                           class="bg-slate-800/50 rounded-2xl p-4 border border-white/5 hover:border-blue-500/30 transition-all group">
                          <div class="flex justify-between items-start mb-2">
                              <h3 class="text-sm font-bold text-white group-hover:text-blue-400 transition-colors cursor-pointer" @click="loadWorkout(item)">
                                  {{ item.title }}
                              </h3>
                              <button @click="deleteHistoryItem(item.id)" class="text-slate-600 hover:text-red-500 transition-colors p-1">
                                  <i class="fa-solid fa-trash-can text-xs"></i>
                              </button>
                          </div>
                          <p class="text-[10px] text-slate-500 mb-3">{{ formatDate(item.created_at) }}</p>
                          <div class="flex flex-wrap gap-1">
                              <span v-for="ex in item.data.slice(0, 3)" :key="ex.id" 
                                    class="text-[9px] bg-slate-700/50 text-slate-400 px-2 py-0.5 rounded-full">
                                  {{ ex.name }}
                              </span>
                              <span v-if="item.data.length > 3" class="text-[9px] text-slate-600">...</span>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </transition>

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
              <label class="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-slate-400 hover:text-white transition-colors cursor-pointer" title="上传视频分析">
                  <i class="fa-solid fa-video"></i>
                  <input type="file" accept="video/*" class="hidden" @change="handleVideoUpload" />
              </label>
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
import axios from 'axios';

export default {
  name: 'HomeView',
  setup() {
    const exercises = ref([]);
    const history = ref([]);
    const showHistory = ref(false);
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
        // 先尝试加载历史记录
        await fetchHistory();
        
        if (history.value.length > 0) {
          // 如果有历史，加载最近的一个
          loadWorkout(history.value[0]);
        } else {
          // 否则使用默认数据
          exercises.value = [
            { id: 101, name: "杠铃深蹲", current: 0, total: 5, tips: "核心收紧；膝盖对准脚尖；背挺直" },
            { id: 102, name: "哑铃卧推", current: 0, total: 4, tips: "沉肩收胛；双脚踩实；挺胸" },
            { id: 103, name: "引体向上", current: 0, total: 3, tips: "背阔肌发力；避免身体晃动" }
          ];
        }
      } catch (e) {
        console.error("加载失败", e);
      } finally {
        loading.value = false;
      }
    };

    const fetchHistory = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/history/');
        history.value = response.data;
      } catch (e) {
        console.error("获取历史失败", e);
      }
    };

    const saveCurrentWorkout = async (title = '') => {
      if (exercises.value.length === 0) return;
      
      const workoutTitle = title || `训练计划 ${new Date().toLocaleDateString()}`;
      try {
        await axios.post('http://localhost:8000/api/history/', {
          title: workoutTitle,
          data: exercises.value
        });
        await fetchHistory();
      } catch (e) {
        console.error("保存失败", e);
      }
    };

    const loadWorkout = (historyItem) => {
      exercises.value = JSON.parse(JSON.stringify(historyItem.data));
      // 重置进度为 0
      exercises.value.forEach(ex => ex.current = 0);
      currentIndex.value = 0;
      showHistory.value = false;
      showSummary.value = false;
    };

    const deleteHistoryItem = async (id) => {
      if (!confirm('确定删除这条历史记录吗？')) return;
      try {
        await axios.delete(`http://localhost:8000/api/history/${id}/`);
        await fetchHistory();
      } catch (e) {
        console.error("删除失败", e);
      }
    };

    const formatDate = (dateStr) => {
      const date = new Date(dateStr);
      return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
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

    const handleVideoUpload = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('video', file);

      loading.value = true;
      try {
        const response = await axios.post('http://localhost:8000/api/analyze-video/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.data.success) {
          exercises.value = response.data.data;
          currentIndex.value = 0;
          showSummary.value = false;
          // 自动保存到历史
          await saveCurrentWorkout(`AI分析 - ${new Date().toLocaleDateString()}`);
        } else {
          alert('分析失败: ' + (response.data.error || '未知错误'));
        }
      } catch (err) {
        console.error('上传失败:', err);
        alert('分析失败，请检查后端服务');
      } finally {
        loading.value = false;
        // 清空 input 方便下次上传同一文件
        event.target.value = '';
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
      history, showHistory,
      incrementProgress, next, prev, parseTips, resetWorkout,
      handleTouchStart, handleTouchEnd, handleVideoUpload,
      fetchHistory, saveCurrentWorkout, loadWorkout, deleteHistoryItem, formatDate
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

.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.3s ease-out;
}
.slide-fade-enter-from, .slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>

