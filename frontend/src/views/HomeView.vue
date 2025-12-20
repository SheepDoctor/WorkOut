<template>
   <div class="w-full max-w-lg h-full flex flex-col p-6 relative overflow-y-auto custom-scrollbar"
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
          <span class="text-xs font-mono text-slate-500" v-if="exercises.length">
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
                            <!-- 编辑模式 -->
                            <div v-if="editingId === item.id" class="flex-1 mr-2">
                                <input 
                                    v-model="editingTitle" 
                                    @keyup.enter="saveEdit(item.id)"
                                    @keyup.esc="cancelEdit"
                                    class="history-edit-input w-full bg-slate-700/50 border border-blue-500/50 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-500"
                                />
                            </div>
                            <!-- 显示模式 -->
                            <h3 v-else class="text-sm font-bold text-white group-hover:text-blue-400 transition-colors cursor-pointer flex-1" @click="loadWorkout(item)">
                                {{ item.title }}
                            </h3>
                            <div class="flex gap-1">
                                <!-- 编辑按钮 -->
                                <button 
                                    v-if="editingId !== item.id"
                                    @click="startEdit(item)" 
                                    class="text-slate-600 hover:text-blue-500 transition-colors p-1"
                                    title="编辑名称">
                                    <i class="fa-solid fa-pencil text-xs"></i>
                                </button>
                                <!-- 保存按钮 -->
                                <button 
                                    v-if="editingId === item.id"
                                    @click="saveEdit(item.id)" 
                                    class="text-blue-500 hover:text-blue-400 transition-colors p-1"
                                    title="保存">
                                    <i class="fa-solid fa-check text-xs"></i>
                                </button>
                                <!-- 取消按钮 -->
                                <button 
                                    v-if="editingId === item.id"
                                    @click="cancelEdit" 
                                    class="text-slate-600 hover:text-slate-400 transition-colors p-1"
                                    title="取消">
                                    <i class="fa-solid fa-xmark text-xs"></i>
                                </button>
                                <!-- 删除按钮 -->
                                <button 
                                    v-if="editingId !== item.id"
                                    @click="deleteHistoryItem(item.id)" 
                                    class="text-slate-600 hover:text-red-500 transition-colors p-1"
                                    title="删除">
                                    <i class="fa-solid fa-trash-can text-xs"></i>
                                </button>
                            </div>
                        </div>
                        <p class="text-[10px] text-slate-500 mb-3">{{ formatDate(item.created_at) }}</p>
                          <div class="flex flex-wrap gap-1">
                              <span v-for="ex in item.exercises.slice(0, 3)" :key="ex.id" 
                                    class="text-[9px] bg-slate-700/50 text-slate-400 px-2 py-0.5 rounded-full">
                                  {{ ex.name }}
                              </span>
                              <span v-if="item.exercises.length > 3" class="text-[9px] text-slate-600">...</span>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </transition>

      <!-- 主内容区 -->
      <div class="flex-1 relative">
          <!-- 无数据时的占位图 -->
          <div v-if="exercises.length === 0 && !loading" class="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
              <div class="w-32 h-32 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-white/5 shadow-inner">
                  <i class="fa-solid fa-dumbbell text-4xl text-slate-700"></i>
              </div>
              <h3 class="text-xl font-bold text-white mb-2">暂无训练计划</h3>
              <p class="text-sm text-slate-500 mb-8 max-w-[240px]">您还没有创建训练计划，可以上传视频进行 AI 分析，或从历史记录中加载。</p>
              <label class="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-bold transition-all shadow-lg shadow-blue-500/25 cursor-pointer">
                  <i class="fa-solid fa-upload mr-2"></i>
                  上传视频开始
                  <input type="file" accept="video/*" class="hidden" @change="handleVideoUpload" />
              </label>
          </div>

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
                          <div class="flex items-center gap-4 text-slate-400">
                              <div class="flex items-center gap-2">
                                  <i class="fa-solid fa-layer-group text-[10px]"></i>
                                  <span class="text-sm">第 {{ currentExercise.current_sets }} 组 / 共 {{ currentExercise.total_sets }} 组</span>
                              </div>
                              <div class="flex items-center gap-2">
                                  <i class="fa-solid fa-repeat text-[10px]"></i>
                                  <span class="text-sm">每组 {{ currentExercise.reps_per_set || 12 }} 次</span>
                              </div>
                          </div>
                      </div>

                      <!-- 视频/进度 切换区域 -->
                      <div class="relative w-full aspect-video mb-8 group" v-if="cameraActive">
                          <div class="absolute inset-0 bg-slate-900 rounded-3xl overflow-hidden border border-white/10 shadow-2xl">
                              <video ref="videoElement" autoplay playsinline class="w-full h-full object-cover"></video>
                              <img v-if="annotatedImage" :src="annotatedImage" class="absolute inset-0 w-full h-full object-cover" />
                              
                              <!-- 实时状态叠加 -->
                              <div class="absolute top-4 left-4 flex flex-col gap-2">
                                  <div :class="['px-4 py-2 rounded-xl font-bold text-sm shadow-lg backdrop-blur-md', 
                                      poseState === 'UP' ? 'bg-blue-500/80 text-white' : 
                                      poseState === 'DOWN' ? 'bg-amber-500/80 text-white' : 
                                      'bg-slate-700/80 text-slate-300']">
                                      {{ getPoseStateText() }}
                                  </div>
                                  <div class="bg-black/50 backdrop-blur-md px-4 py-2 rounded-xl border border-white/10">
                                      <span class="text-xs text-slate-400 uppercase mr-2">次数</span>
                                      <span class="text-xl font-bold text-emerald-400">{{ reps }} / {{ currentExercise.reps_per_set || 12 }}</span>
                                  </div>
                              </div>

                              <button @click="stopCamera" class="absolute top-4 right-4 w-10 h-10 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded-xl flex items-center justify-center transition-all backdrop-blur-md border border-red-500/20">
                                  <i class="fa-solid fa-xmark"></i>
                              </button>
                          </div>
                      </div>

                      <!-- 环形进度 (当摄像头未开启时) -->
                      <div v-else class="relative w-48 h-48 mx-auto mb-10 flex items-center justify-center">
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

                      <!-- AI 建议 (仅在摄像头开启时显示) -->
                      <div v-if="cameraActive && feedback.length > 0" class="mb-6 space-y-2">
                          <div v-for="(item, fIndex) in feedback.slice(0, 2)" :key="fIndex" 
                               :class="['flex items-center gap-3 p-3 rounded-2xl border text-xs transition-all',
                                        item.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 
                                        item.type === 'warning' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' : 
                                        'bg-blue-500/10 border-blue-500/20 text-blue-400']">
                              <i :class="['fa-solid', item.type === 'success' ? 'fa-circle-check' : (item.type === 'warning' ? 'fa-triangle-exclamation' : 'fa-circle-info')]"></i>
                              <span>{{ item.message }}</span>
                          </div>
                      </div>

                      <!-- 开始训练按钮 (当摄像头未开启时) -->
                      <button v-if="!cameraActive && !isCompleted" @click="startCamera" 
                              class="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-bold transition-all shadow-lg shadow-blue-500/25 mb-8 flex items-center justify-center gap-2">
                          <i class="fa-solid fa-camera"></i>
                          开始训练
                      </button>

                      <!-- 动作要领 -->
                      <div class="bg-slate-900/40 rounded-3xl p-6 border border-white/5 mb-6">
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

                      <!-- 训练历史 -->
                      <div class="bg-slate-900/40 rounded-3xl p-6 border border-white/5">
                          <div class="flex items-center gap-2 mb-4 text-xs font-bold text-slate-500 tracking-widest uppercase">
                              <i class="fa-solid fa-clock-rotate-left text-emerald-400"></i> 训练历史
                          </div>
                          <div v-if="exerciseHistory.length === 0" class="text-center py-8 text-slate-600">
                              <i class="fa-solid fa-inbox text-2xl mb-2 opacity-30"></i>
                              <p class="text-xs">暂无训练记录</p>
                          </div>
                          <div v-else class="space-y-2 max-h-40 overflow-y-auto pr-2">
                              <div v-for="(log, logIndex) in exerciseHistory.slice(0, 5)" :key="log.id" 
                                   class="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-white/5 hover:border-emerald-500/30 transition-all">
                                  <div class="flex-1">
                                      <div class="flex items-center gap-2 mb-1">
                                          <span class="text-xs text-slate-400">{{ formatDate(log.start_time) }}</span>
                                          <span :class="['px-2 py-0.5 rounded-full text-[9px] font-bold',
                                              log.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                                              log.status === 'interrupted' ? 'bg-amber-500/20 text-amber-400' :
                                              'bg-red-500/20 text-red-400']">
                                              {{ log.status === 'completed' ? '已完成' : log.status === 'interrupted' ? '已中断' : '失败' }}
                                          </span>
                                      </div>
                                      <div class="flex items-center gap-3 text-xs text-slate-300">
                                          <span v-if="log.target_sets" class="flex items-center gap-1">
                                              <i class="fa-solid fa-layer-group text-[8px]"></i>
                                              {{ log.set_index || 1 }}/{{ log.target_sets }} 组
                                          </span>
                                          <span v-if="log.target_reps" class="flex items-center gap-1">
                                              <i class="fa-solid fa-repeat text-[8px]"></i>
                                              {{ log.reps_count }}/{{ log.target_reps }} 次
                                          </span>
                                          <span v-if="log.duration" class="flex items-center gap-1">
                                              <i class="fa-solid fa-clock text-[8px]"></i>
                                              {{ Math.floor(log.duration / 60) }}:{{ String(log.duration % 60).padStart(2, '0') }}
                                          </span>
                                      </div>
                                  </div>
                                  <div v-if="log.ai_score !== null && log.ai_score !== undefined" 
                                       class="ml-3 px-2 py-1 rounded-lg bg-blue-500/20 border border-blue-500/30">
                                      <span class="text-xs font-bold text-blue-400">{{ Math.round(log.ai_score) }}</span>
                                  </div>
                              </div>
                              <div v-if="exerciseHistory.length > 5" class="text-center pt-2">
                                  <span class="text-[10px] text-slate-600">还有 {{ exerciseHistory.length - 5 }} 条记录</span>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>
          </transition>
      </div>

      <!-- 底部留白，防止内容被固定按钮遮挡 -->
      <div class="h-32 shrink-0"></div>

       <!-- 底部控制 -->
       <footer class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-lg px-6 py-8 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent z-40 flex items-center justify-between gap-4">
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
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
    const currentWorkoutId = ref(null); // 当前计划 ID (WorkoutPlan)
    const currentLogId = ref(null);    // 当前训练日志 ID (WorkoutLog)
    const startTime = ref(null);      // 训练开始时间
    const timerInterval = ref(null);
    const duration = ref(0);          // 持续时长（秒）
    const exerciseHistory = ref([]);   // 当前动作的训练历史

    // 编辑相关状态
    const editingId = ref(null);      // 正在编辑的计划ID
    const editingTitle = ref('');     // 编辑中的标题

    // --- 摄像头与分析状态 ---
    const cameraActive = ref(false);
    const analyzing = ref(false);
    const error = ref(null);
    const feedback = ref([]);
    const annotatedImage = ref(null);
    const stream = ref(null);
    const reps = ref(0); // 当前组的次数
    const poseState = ref('UNKNOWN');
    const isDown = ref(false);
    const videoElement = ref(null);

    // 动作类型映射
    const getExerciseType = (name) => {
      if (name.includes('深蹲')) return 'squat';
      if (name.includes('弯举')) return 'curl';
      if (name.includes('推肩') || name.includes('卧推')) return 'press';
      return 'squat'; // 默认
    };

    const getPoseStateText = () => {
      const type = getExerciseType(currentExercise.value.name);
      const map = {
        'UP': type === 'squat' ? '站立 (UP)' : (type === 'press' ? '推起 (UP)' : '举起 (UP)'),
        'DOWN': type === 'squat' ? '下蹲 (DOWN)' : '放下 (DOWN)',
        'TRANSITION': '动作中...',
        'UNKNOWN': '准备中'
      };
      return map[poseState.value] || poseState.value;
    };

    const startCamera = async () => {
      try {
        error.value = null;
        const s = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
          }
        });
        stream.value = s;
        cameraActive.value = true;
        reps.value = 0;
        isDown.value = false;
        
        // 记录开始时间和重置时长
        startTime.value = new Date();
        duration.value = 0;
        
        // 创建训练日志
        await createWorkoutLog();
        
        // 这里的 videoElement 引用会在模板渲染后可用
        setTimeout(() => {
          if (videoElement.value) {
            videoElement.value.srcObject = s;
            analyzeLoop();
          }
        }, 100);
      } catch (err) {
        error.value = '无法访问摄像头，请检查权限设置';
        console.error('Camera error:', err);
      }
    };

    const stopCamera = async (status = 'interrupted') => {
      // 如果 status 是事件对象（点击关闭按钮时），则默认为 'interrupted'
      const finalStatus = typeof status === 'string' ? status : 'interrupted';
      
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop());
        stream.value = null;
      }
      cameraActive.value = false;
      annotatedImage.value = null;
      feedback.value = [];

      // 结束日志记录
      if (startTime.value) {
        duration.value = Math.round((new Date() - startTime.value) / 1000);
        await updateWorkoutLog(finalStatus);
        startTime.value = null;
      }
    };

    const createWorkoutLog = async () => {
      try {
        const plan = history.value.find(p => p.id === currentWorkoutId.value);
        const response = await axios.post('http://localhost:8000/api/logs/', {
          plan_title: plan ? plan.title : '个人练习',
          action_name: currentExercise.value.name,
          set_index: currentExercise.value.current_sets + 1,
          reps_count: 0,
          status: 'interrupted',
          exercise_id: currentExercise.value.id,
          target_reps: currentExercise.value.reps_per_set || 12,
          target_sets: currentExercise.value.total_sets
        });
        currentLogId.value = response.data.id;
        console.log('训练记录已创建:', currentLogId.value);
      } catch (e) {
        console.error("创建训练日志失败", e);
      }
    };

    const updateWorkoutLog = async (finalStatus) => {
      if (!currentLogId.value) return;
      try {
        await axios.patch(`http://localhost:8000/api/logs/${currentLogId.value}/`, {
          reps_count: reps.value,
          duration: duration.value,
          status: finalStatus,
          exercise_id: currentExercise.value.id,
          target_reps: currentExercise.value.reps_per_set || 12,
          target_sets: currentExercise.value.total_sets
        });
        console.log('训练记录已更新:', currentLogId.value, '状态:', finalStatus);
        currentLogId.value = null;
      } catch (e) {
        console.error("更新训练日志失败", e);
      }
    };

    const analyzeLoop = async () => {
      if (!cameraActive.value || showSummary.value) return;
      if (!analyzing.value) {
        await captureAndAnalyze();
      }
      requestAnimationFrame(analyzeLoop);
    };

    const captureAndAnalyze = async () => {
      if (!cameraActive.value || !videoElement.value) return;
      analyzing.value = true;
      try {
        const canvas = document.createElement('canvas');
        const video = videoElement.value;
        if (video.readyState !== 4) {
          analyzing.value = false;
          return;
        }
        canvas.width = 480;
        canvas.height = video.videoHeight * (480 / video.videoWidth);
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg', 0.5);

        const response = await axios.post('http://localhost:8000/api/analyze-pose/', {
          image: imageData,
          exercise_type: getExerciseType(currentExercise.value.name)
        });

        if (response.data.success) {
          const data = response.data.data;
          feedback.value = data.feedback || [];
          annotatedImage.value = data.annotated_image;
          updateWorkoutState(data.pose_state);
        }
      } catch (err) {
        console.error('Analysis error:', err);
      } finally {
        analyzing.value = false;
      }
    };

    const updateWorkoutState = (currentState) => {
      const type = getExerciseType(currentExercise.value.name);
      if (type === 'squat') {
        if (currentState === 'DOWN') {
          isDown.value = true;
        } else if (currentState === 'UP' && isDown.value) {
          incrementReps();
          isDown.value = false;
        }
      } else if (type === 'curl' || type === 'press') {
        if (currentState === 'UP') {
          isDown.value = true;
        } else if (currentState === 'DOWN' && isDown.value) {
          incrementReps();
          isDown.value = false;
        }
      }
      poseState.value = currentState;
    };

    const incrementReps = () => {
      reps.value++;
      const targetReps = currentExercise.value.reps_per_set || 12;
      
      if (reps.value >= targetReps) {
        stopCamera('completed'); // 完成一组，停止视频监督
        incrementProgress();
        reps.value = 0;
        feedback.value = [{ type: 'success', message: `恭喜！完成一组。已为您停止视频并同步记录。` }];
      }
    };

    // --- 1. 后端交互函数 ---

    const fetchWorkout = async () => {
      loading.value = true;
      try {
        // 仅加载历史记录，不自动加载计划
        await fetchHistory();
      } catch (e) {
        console.error("加载失败", e);
      } finally {
        loading.value = false;
      }
    };

    const fetchHistory = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/plans/');
        history.value = Array.isArray(response.data) ? response.data : [];
      } catch (e) {
        console.error("获取计划失败", e);
        history.value = [];
      }
    };

    const fetchExerciseHistory = async () => {
      if (!currentExercise.value) {
        exerciseHistory.value = [];
        return;
      }
      try {
        const params = {};
        // 优先使用 exercise_id 过滤
        if (currentExercise.value.id) {
          params.exercise_id = currentExercise.value.id;
        } else if (currentExercise.value.name) {
          // 如果没有 id，使用 action_name 过滤
          params.action_name = currentExercise.value.name;
        }
        
        const response = await axios.get('http://localhost:8000/api/logs/', { params });
        // 后端已经按时间倒序排列，只取最近10条
        const allLogs = Array.isArray(response.data) ? response.data : [];
        exerciseHistory.value = allLogs.slice(0, 10);
      } catch (e) {
        console.error("获取训练历史失败", e);
        exerciseHistory.value = [];
      }
    };

    const saveCurrentWorkout = async (title = '') => {
      if (exercises.value.length === 0) return;
      
      const workoutTitle = title || `训练计划 ${new Date().toLocaleDateString()}`;
      try {
        const response = await axios.post('http://localhost:8000/api/plans/', {
          title: workoutTitle,
          exercises: exercises.value
        });
        currentWorkoutId.value = response.data.id; // 保存新创建的 ID
        await fetchHistory();
      } catch (e) {
        console.error("保存失败", e);
      }
    };

    const loadWorkout = (historyItem) => {
      if (!historyItem) return;
      currentWorkoutId.value = historyItem.id; // 记录当前加载的训练 ID
      // 兼容旧数据的 data 字段，优先使用 exercises
      const rawExercises = historyItem.exercises || historyItem.data || [];
      exercises.value = Array.isArray(rawExercises) ? JSON.parse(JSON.stringify(rawExercises)) : [];
      // 注意：这里不再重置进度，而是保留数据库中的进度
      currentIndex.value = 0;
      showHistory.value = false;
      showSummary.value = false;
      // 加载当前动作的历史记录
      fetchExerciseHistory();
    };

    const deleteHistoryItem = async (id) => {
      if (!confirm('确定删除这个训练计划吗？')) return;
      try {
        await axios.delete(`http://localhost:8000/api/plans/${id}/`);
        if (currentWorkoutId.value === id) {
          currentWorkoutId.value = null;
        }
        await fetchHistory();
      } catch (e) {
        console.error("删除失败", e);
      }
    };

    const startEdit = (item) => {
      editingId.value = item.id;
      editingTitle.value = item.title;
      // 等待 DOM 更新后聚焦输入框
      setTimeout(() => {
        const inputs = document.querySelectorAll('.history-edit-input');
        if (inputs.length > 0) {
          // 找到当前正在编辑的那个 input
          const currentInput = Array.from(inputs).find(input => {
            const parent = input.closest('.bg-slate-800\\/50');
            return parent && parent.querySelector('.text-sm')?.textContent === item.title || true;
          });
          if (currentInput) {
            currentInput.focus();
            currentInput.select();
          }
        }
      }, 100);
    };

    const cancelEdit = () => {
      editingId.value = null;
      editingTitle.value = '';
    };

    const saveEdit = async (id) => {
      if (!editingTitle.value.trim()) {
        alert('计划名称不能为空');
        return;
      }
      try {
        await axios.patch(`http://localhost:8000/api/plans/${id}/`, {
          title: editingTitle.value.trim()
        });
        const item = history.value.find(h => h.id === id);
        if (item) {
          item.title = editingTitle.value.trim();
        }
        cancelEdit();
      } catch (e) {
        console.error("更新失败", e);
        alert('更新失败，请重试');
      }
    };

    const formatDate = (dateStr) => {
      const date = new Date(dateStr);
      return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
    };

    const syncProgress = async (exercise) => {
      if (!currentWorkoutId.value) return;
      
      syncing.value = true;
      try {
        // 更新数据库中对应的记录
        await axios.patch(`http://localhost:8000/api/plans/${currentWorkoutId.value}/`, {
          exercises: exercises.value
        });
        console.log(`已同步 ${exercise.name} 进度到数据库`);
      } catch (e) {
        console.error("同步数据库失败", e);
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
          const result = response.data.data;
          exercises.value = result.exercises || [];
          currentIndex.value = 0;
          showSummary.value = false;
          // 自动保存到历史，使用 AI 生成的标题
          const aiTitle = result.title || `AI分析 - ${new Date().toLocaleDateString()}`;
          await saveCurrentWorkout(aiTitle);
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
      if (!currentExercise.value.total_sets) return 0;
      return Math.min(Math.round((currentExercise.value.current_sets / currentExercise.value.total_sets) * 100), 100);
    });
    const isCompleted = computed(() => currentExercise.value.current_sets >= currentExercise.value.total_sets);

    const incrementProgress = () => {
      if (isCompleted.value || autoJumping.value) return;
      // 确保 current_sets 存在
      if (currentExercise.value.current_sets === undefined) {
        currentExercise.value.current_sets = 0;
      }
      currentExercise.value.current_sets++;
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
        fetchExerciseHistory(); // 切换动作时加载历史
      }
    };

    const prev = () => {
      if (currentIndex.value > 0) {
        transitionName.value = 'slide-left';
        currentIndex.value--;
        autoJumping.value = false;
        fetchExerciseHistory(); // 切换动作时加载历史
      }
    };

    const parseTips = (tips) => {
      if (!tips) return [];
      return Array.isArray(tips) ? tips : tips.split(/[；;。]/).filter(t => t.trim());
    };

    const resetWorkout = () => {
      exercises.value.forEach(e => e.current_sets = 0);
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

    // 监听当前动作变化，自动加载历史记录
    watch(() => currentExercise.value?.id, (newId) => {
      if (newId) {
        fetchExerciseHistory();
      }
    }, { immediate: true });

    onMounted(fetchWorkout);
    onBeforeUnmount(stopCamera);

    return {
      exercises, currentIndex, currentExercise, currentPercent, isCompleted,
      loading, syncing, autoJumping, showSummary, transitionName,
      history, showHistory, exerciseHistory,
      cameraActive, analyzing, error, feedback, annotatedImage, reps, poseState, videoElement,
      startCamera, stopCamera, getPoseStateText,
      incrementProgress, next, prev, parseTips, resetWorkout,
      handleTouchStart, handleTouchEnd, handleVideoUpload,
      fetchHistory, saveCurrentWorkout, loadWorkout, deleteHistoryItem, formatDate,
      editingId, editingTitle, startEdit, cancelEdit, saveEdit
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

 /* 自定义滚动条样式 */
 .custom-scrollbar::-webkit-scrollbar {
   width: 4px;
 }
 .custom-scrollbar::-webkit-scrollbar-track {
   background: transparent;
 }
 .custom-scrollbar::-webkit-scrollbar-thumb {
   background: rgba(255, 255, 255, 0.1);
   border-radius: 10px;
 }
 .custom-scrollbar::-webkit-scrollbar-thumb:hover {
   background: rgba(255, 255, 255, 0.2);
 }
 </style>

