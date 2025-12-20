<template>
  <div class="w-full max-w-lg h-full flex flex-col p-6 relative overflow-y-auto custom-scrollbar">
    <!-- 顶部标题栏 -->
    <header class="mb-8 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="$router.push('/')" class="text-slate-400 hover:text-white transition-colors">
          <i class="fa-solid fa-arrow-left"></i>
        </button>
        <h1 class="text-2xl font-bold text-white">荣誉殿堂</h1>
      </div>
      <div class="text-xs text-slate-500 font-mono">
        成就 {{ unlockedCount }} / {{ totalCount }}
      </div>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- 成就列表 -->
    <div v-else class="space-y-8">
      <!-- 基础性能类 -->
      <section>
        <div class="flex items-center gap-2 mb-6">
          <div class="w-1 h-8 bg-gradient-to-b from-blue-500 to-blue-400 rounded-full"></div>
          <h2 class="text-lg font-bold text-white">基础性能类</h2>
          <span class="text-xs text-slate-500 ml-auto">Performance Modules</span>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div v-for="achievement in performanceAchievements" :key="achievement.id"
               :class="['achievement-card p-5 rounded-3xl border-2 transition-all cursor-pointer group',
                        achievement.unlocked ? 'bg-gradient-to-br from-cyan-500/25 to-blue-600/15 border-cyan-400/60 hover:border-cyan-300 hover:shadow-xl hover:shadow-cyan-500/30' : 
                        'bg-gradient-to-br from-indigo-900/30 to-slate-800/50 border-indigo-700/40 hover:border-indigo-600']"
               @click="showAchievementDetail(achievement)">
            <div class="flex flex-col items-center text-center">
              <!-- 勋章图标 -->
              <div :class="['w-20 h-20 rounded-full flex items-center justify-center mb-4 transition-all',
                           achievement.unlocked ? 'bg-gradient-to-br from-cyan-400 to-blue-500 shadow-2xl shadow-cyan-500/60' : 
                           'bg-indigo-900/40']">
                <i :class="[achievement.icon, 'text-3xl',
                           achievement.unlocked ? 'text-white' : 'text-slate-600']"></i>
              </div>
              <!-- 成就名称 -->
              <h3 :class="['text-sm font-bold mb-2',
                          achievement.unlocked ? 'text-white' : 'text-slate-500']">
                {{ achievement.name }}
              </h3>
              <!-- 进度条 -->
              <div v-if="!achievement.unlocked && achievement.progress !== undefined" 
                   class="w-full bg-indigo-900/40 rounded-full h-1.5 mb-2">
                <div class="bg-gradient-to-r from-cyan-400 to-blue-500 h-full rounded-full transition-all duration-500 shadow-lg shadow-cyan-500/50"
                     :style="{ width: `${Math.min(achievement.progress, 100)}%` }"></div>
              </div>
              <!-- 解锁状态 -->
              <div v-if="achievement.unlocked" 
                   class="flex items-center gap-1 text-[10px] text-cyan-300 font-bold uppercase tracking-widest">
                <i class="fa-solid fa-check-circle"></i>
                <span>已解锁</span>
              </div>
              <div v-else class="text-[10px] text-slate-600 uppercase tracking-widest">
                {{ achievement.progress !== undefined ? `${Math.round(achievement.progress)}%` : '未解锁' }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 稀有进化类 -->
      <section>
        <div class="flex items-center gap-2 mb-6">
          <div class="w-1 h-8 bg-gradient-to-b from-purple-500 to-purple-400 rounded-full"></div>
          <h2 class="text-lg font-bold text-white">稀有进化类</h2>
          <span class="text-xs text-slate-500 ml-auto">Evolutionary Milestones</span>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div v-for="achievement in evolutionAchievements" :key="achievement.id"
               :class="['achievement-card p-5 rounded-3xl border-2 transition-all cursor-pointer group',
                        achievement.unlocked ? 'bg-gradient-to-br from-purple-500/25 to-fuchsia-600/15 border-purple-400/60 hover:border-purple-300 hover:shadow-xl hover:shadow-purple-500/30' : 
                        'bg-gradient-to-br from-indigo-900/30 to-slate-800/50 border-indigo-700/40 hover:border-indigo-600']"
               @click="showAchievementDetail(achievement)">
            <div class="flex flex-col items-center text-center">
              <!-- 勋章图标 -->
              <div :class="['w-20 h-20 rounded-full flex items-center justify-center mb-4 transition-all relative',
                           achievement.unlocked ? 'bg-gradient-to-br from-purple-400 to-fuchsia-500 shadow-2xl shadow-purple-500/60' : 
                           'bg-indigo-900/40']">
                <i :class="[achievement.icon, 'text-3xl',
                           achievement.unlocked ? 'text-white' : 'text-slate-600']"></i>
                <!-- 稀有标识 -->
                <div v-if="achievement.unlocked" 
                     class="absolute -top-1 -right-1 w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center border-2 border-slate-900">
                  <i class="fa-solid fa-star text-[10px] text-white"></i>
                </div>
              </div>
              <!-- 成就名称 -->
              <h3 :class="['text-sm font-bold mb-2',
                          achievement.unlocked ? 'text-white' : 'text-slate-500']">
                {{ achievement.name }}
              </h3>
              <!-- 进度条 -->
              <div v-if="!achievement.unlocked && achievement.progress !== undefined" 
                   class="w-full bg-indigo-900/40 rounded-full h-1.5 mb-2">
                <div class="bg-gradient-to-r from-purple-400 to-fuchsia-500 h-full rounded-full transition-all duration-500 shadow-lg shadow-purple-500/50"
                     :style="{ width: `${Math.min(achievement.progress, 100)}%` }"></div>
              </div>
              <!-- 解锁状态 -->
              <div v-if="achievement.unlocked" 
                   class="flex items-center gap-1 text-[10px] text-purple-300 font-bold uppercase tracking-widest">
                <i class="fa-solid fa-check-circle"></i>
                <span>已解锁</span>
              </div>
              <div v-else class="text-[10px] text-slate-600 uppercase tracking-widest">
                {{ achievement.progress !== undefined ? `${Math.round(achievement.progress)}%` : '未解锁' }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 其他成就类 -->
      <section v-if="otherAchievements.length > 0">
        <div class="flex items-center gap-2 mb-6">
          <div class="w-1 h-8 bg-gradient-to-b from-emerald-500 to-emerald-400 rounded-full"></div>
          <h2 class="text-lg font-bold text-white">其他成就</h2>
          <span class="text-xs text-slate-500 ml-auto">Additional Achievements</span>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div v-for="achievement in otherAchievements" :key="achievement.id"
               :class="['achievement-card p-5 rounded-3xl border-2 transition-all cursor-pointer group',
                        achievement.unlocked ? 'bg-gradient-to-br from-emerald-400/25 to-teal-600/15 border-emerald-400/60 hover:border-emerald-300 hover:shadow-xl hover:shadow-emerald-500/30' : 
                        'bg-gradient-to-br from-indigo-900/30 to-slate-800/50 border-indigo-700/40 hover:border-indigo-600']"
               @click="showAchievementDetail(achievement)">
            <div class="flex flex-col items-center text-center">
              <!-- 勋章图标 -->
              <div :class="['w-20 h-20 rounded-full flex items-center justify-center mb-4 transition-all',
                           achievement.unlocked ? 'bg-gradient-to-br from-emerald-400 to-teal-500 shadow-2xl shadow-emerald-500/60' : 
                           'bg-indigo-900/40']">
                <i :class="[achievement.icon, 'text-3xl',
                           achievement.unlocked ? 'text-white' : 'text-slate-600']"></i>
              </div>
              <!-- 成就名称 -->
              <h3 :class="['text-sm font-bold mb-2',
                          achievement.unlocked ? 'text-white' : 'text-slate-500']">
                {{ achievement.name }}
              </h3>
              <!-- 进度条 -->
              <div v-if="!achievement.unlocked && achievement.progress !== undefined" 
                   class="w-full bg-indigo-900/40 rounded-full h-1.5 mb-2">
                <div class="bg-gradient-to-r from-emerald-400 to-teal-500 h-full rounded-full transition-all duration-500 shadow-lg shadow-emerald-500/50"
                     :style="{ width: `${Math.min(achievement.progress, 100)}%` }"></div>
              </div>
              <!-- 解锁状态 -->
              <div v-if="achievement.unlocked" 
                   class="flex items-center gap-1 text-[10px] text-emerald-300 font-bold uppercase tracking-widest">
                <i class="fa-solid fa-check-circle"></i>
                <span>已解锁</span>
              </div>
              <div v-else class="text-[10px] text-slate-600 uppercase tracking-widest">
                {{ achievement.progress !== undefined ? `${Math.round(achievement.progress)}%` : '未解锁' }}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 成就详情弹窗 -->
    <transition name="fade">
      <div v-if="selectedAchievement" 
           class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-xl flex items-center justify-center p-6"
           @click.self="selectedAchievement = null">
        <div class="max-w-md w-full bg-gradient-to-br from-indigo-900/90 to-purple-900/90 rounded-[2.5rem] border border-cyan-400/20 overflow-hidden shadow-2xl shadow-cyan-500/20 backdrop-blur-xl">
          <div class="p-8">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-2xl font-bold text-white">成就详情</h2>
              <button @click="selectedAchievement = null" 
                      class="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center transition-all">
                <i class="fa-solid fa-xmark text-slate-400"></i>
              </button>
            </div>

            <div class="text-center mb-6">
              <!-- 大图标 -->
              <div :class="['w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-4',
                           selectedAchievement.unlocked ? 
                           (selectedAchievement.category === 'evolution' ? 'bg-gradient-to-br from-purple-400 to-fuchsia-500 shadow-2xl shadow-purple-500/60' :
                            selectedAchievement.category === 'other' ? 'bg-gradient-to-br from-emerald-400 to-teal-500 shadow-2xl shadow-emerald-500/60' :
                            'bg-gradient-to-br from-cyan-400 to-blue-500 shadow-2xl shadow-cyan-500/60') :
                           'bg-indigo-900/40']">
                <i :class="[selectedAchievement.icon, 'text-5xl',
                           selectedAchievement.unlocked ? 'text-white' : 'text-slate-600']"></i>
              </div>
              <h3 class="text-xl font-bold text-white mb-2">{{ selectedAchievement.name }}</h3>
              <p class="text-sm text-slate-400 leading-relaxed">{{ selectedAchievement.description }}</p>
            </div>

            <!-- 进度信息 -->
            <div v-if="selectedAchievement.progress !== undefined" class="bg-indigo-900/40 rounded-2xl p-4 mb-6 border border-cyan-500/20">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs text-slate-400 uppercase font-bold tracking-widest">完成进度</span>
                <span class="text-sm font-bold text-white">{{ Math.round(selectedAchievement.progress) }}%</span>
              </div>
              <div class="w-full bg-slate-900/50 rounded-full h-2">
                <div :class="['h-full rounded-full transition-all duration-500',
                             selectedAchievement.category === 'evolution' ? 'bg-gradient-to-r from-purple-400 to-fuchsia-500 shadow-lg shadow-purple-500/50' :
                             selectedAchievement.category === 'other' ? 'bg-gradient-to-r from-emerald-400 to-teal-500 shadow-lg shadow-emerald-500/50' :
                             'bg-gradient-to-r from-cyan-400 to-blue-500 shadow-lg shadow-cyan-500/50']"
                     :style="{ width: `${Math.min(selectedAchievement.progress, 100)}%` }"></div>
              </div>
            </div>

            <!-- 解锁时间 -->
            <div v-if="selectedAchievement.unlocked && selectedAchievement.unlockedAt" 
                 class="text-center text-xs text-slate-500 mb-6">
              解锁时间: {{ formatDate(selectedAchievement.unlockedAt) }}
            </div>

            <button @click="selectedAchievement = null" 
                    class="w-full py-4 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 border border-cyan-400/30 text-white rounded-2xl font-bold transition-all hover:shadow-lg hover:shadow-cyan-500/30">
              我知道了
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 底部留白 -->
    <div class="h-20 shrink-0"></div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'AchievementsView',
  setup() {
    const loading = ref(true);
    const achievements = ref([]);

    // 从后端获取成就数据
    const fetchAchievements = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/achievements/');
        achievements.value = response.data.achievements || [];
      } catch (error) {
        console.error('获取成就数据失败:', error);
        // 如果API不存在，使用默认数据
        achievements.value = getDefaultAchievements();
      } finally {
        loading.value = false;
      }
    };

    // 默认成就数据（如果后端API不存在）
    const getDefaultAchievements = () => {
      return [
        // 基础性能类
        {
          id: 'first_training',
          name: '动力源激活',
          description: '完成首次训练，开启你的健身之旅！',
          icon: 'fa-solid fa-bolt',
          category: 'performance',
          unlocked: false,
          progress: 0
        },
        {
          id: 'calorie_500',
          name: '热能管理',
          description: '单次训练消耗超过 500 大卡，燃烧你的卡路里！',
          icon: 'fa-solid fa-fire',
          category: 'performance',
          unlocked: false,
          progress: 0
        },
        {
          id: 'streak_7',
          name: '频率同步',
          description: '连续 7 天完成训练计划，保持你的训练节奏！',
          icon: 'fa-solid fa-calendar-check',
          category: 'performance',
          unlocked: false,
          progress: 0
        },
        // 稀有进化类
        {
          id: 'boeing_747',
          name: '人类极限模拟',
          description: '累计举起重量相当于一架波音 747（约 183,500 公斤）',
          icon: 'fa-solid fa-plane',
          category: 'evolution',
          unlocked: false,
          progress: 0
        },
        {
          id: 'all_muscles',
          name: '赛博格形态',
          description: '全身所有肌肉群（3D模型上）均已达到"激活"状态',
          icon: 'fa-solid fa-robot',
          category: 'evolution',
          unlocked: false,
          progress: 0
        },
        // 其他成就
        {
          id: 'perfect_form',
          name: '完美姿态',
          description: '连续 10 次训练获得 AI 评分 90 分以上',
          icon: 'fa-solid fa-star',
          category: 'other',
          unlocked: false,
          progress: 0
        },
        {
          id: 'marathon',
          name: '马拉松训练',
          description: '单次训练时长超过 60 分钟',
          icon: 'fa-solid fa-stopwatch',
          category: 'other',
          unlocked: false,
          progress: 0
        },
        {
          id: 'century',
          name: '百次挑战',
          description: '单次训练完成 100 次动作',
          icon: 'fa-solid fa-hundred-points',
          category: 'other',
          unlocked: false,
          progress: 0
        },
        {
          id: 'streak_30',
          name: '月度坚持',
          description: '连续 30 天完成训练计划',
          icon: 'fa-solid fa-calendar-days',
          category: 'other',
          unlocked: false,
          progress: 0
        },
        {
          id: 'early_bird',
          name: '早起鸟',
          description: '连续 7 天在早上 8 点前完成训练',
          icon: 'fa-solid fa-sun',
          category: 'other',
          unlocked: false,
          progress: 0
        },
        {
          id: 'night_owl',
          name: '夜猫子',
          description: '连续 7 天在晚上 10 点后完成训练',
          icon: 'fa-solid fa-moon',
          category: 'other',
          unlocked: false,
          progress: 0
        },
        {
          id: 'variety',
          name: '动作大师',
          description: '完成过 20 种不同的训练动作',
          icon: 'fa-solid fa-dumbbell',
          category: 'other',
          unlocked: false,
          progress: 0
        }
      ];
    };

    // 分类成就
    const performanceAchievements = computed(() => {
      return achievements.value.filter(a => a.category === 'performance');
    });

    const evolutionAchievements = computed(() => {
      return achievements.value.filter(a => a.category === 'evolution');
    });

    const otherAchievements = computed(() => {
      return achievements.value.filter(a => a.category === 'other');
    });

    // 统计
    const unlockedCount = computed(() => {
      return achievements.value.filter(a => a.unlocked).length;
    });

    const totalCount = computed(() => {
      return achievements.value.length;
    });

    // 成就详情
    const selectedAchievement = ref(null);

    const showAchievementDetail = (achievement) => {
      selectedAchievement.value = achievement;
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
    };

    onMounted(() => {
      fetchAchievements();
    });

    return {
      loading,
      achievements,
      performanceAchievements,
      evolutionAchievements,
      otherAchievements,
      unlockedCount,
      totalCount,
      selectedAchievement,
      showAchievementDetail,
      formatDate
    };
  }
};
</script>

<style scoped>
.achievement-card {
  backdrop-filter: blur(12px);
  transition: transform 0.2s, box-shadow 0.2s;
}

.achievement-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 自定义滚动条样式 */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(34, 211, 238, 0.9) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(30, 27, 75, 0.4);
  border-radius: 999px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(34, 211, 238, 0.9), rgba(59, 130, 246, 0.9));
  border-radius: 999px;
  border: 1px solid rgba(30, 27, 75, 0.5);
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.5);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(103, 232, 249, 1), rgba(96, 165, 250, 1));
  box-shadow: 0 0 15px rgba(34, 211, 238, 0.8);
}
</style>

