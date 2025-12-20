<template>
   <div class="w-full max-w-lg h-full flex flex-col p-6 relative overflow-y-auto custom-scrollbar"
        @touchstart="handleTouchStart"
        @touchend="handleTouchEnd">

      <!-- 加载状态 -->
      <div v-if="loading" class="absolute inset-0 z-50 bg-slate-950 flex flex-col items-center justify-center p-8">
          <div class="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-10"></div>
          
          <div class="w-full max-w-[240px] space-y-4">
              <div v-for="(step, index) in loadingSteps" :key="index" 
                   class="flex items-center gap-4 transition-all duration-500"
                   :class="index <= currentLoadingStep ? 'opacity-100 translate-x-0' : 'opacity-20 -translate-x-2'">
                  <div class="w-5 h-5 flex items-center justify-center">
                      <i v-if="index < currentLoadingStep" class="fa-solid fa-circle-check text-emerald-500 text-sm"></i>
                      <i v-else-if="index === currentLoadingStep" class="fa-solid fa-circle-notch animate-spin text-blue-500 text-sm"></i>
                      <div v-else class="w-1.5 h-1.5 rounded-full bg-slate-800"></div>
                  </div>
                  <span :class="['text-xs tracking-widest uppercase font-medium', 
                                 index === currentLoadingStep ? 'text-white' : 'text-slate-500']">
                      {{ step }}
                  </span>
              </div>
          </div>
          
          <p class="mt-12 text-[10px] text-slate-600 uppercase tracking-[0.2em] animate-pulse">
              AI Coach is processing...
          </p>
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
                  <div class="absolute right-0 top-0 bottom-0 w-80 bg-slate-900 shadow-2xl p-6 overflow-y-auto custom-scrollbar">
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
                      <div class="mb-10">
                          <div class="flex items-center gap-3 mb-3">
                              <span class="px-3 py-1 bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold tracking-widest uppercase rounded-full">
                                  {{ isCompleted ? '动作已完成' : '训练中' }}
                              </span>
                              <div v-if="!isCompleted" class="flex gap-1">
                                  <span class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></span>
                                  <span class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                  <span class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                              </div>
                          </div>
                          <h1 class="text-3xl font-extrabold text-white mb-3 leading-tight tracking-tight">
                              {{ currentExercise.name }}
                          </h1>
                          <!-- 训练部位标签 -->
                          <div v-if="currentExercise.muscle_group" class="mb-6">
                              <span class="inline-flex items-center gap-2 px-4 py-1.5 bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-bold tracking-widest uppercase rounded-full">
                                  <i class="fa-solid fa-dumbbell text-[10px]"></i>
                                  {{ currentExercise.muscle_group }}
                              </span>
                          </div>
                          <div v-else class="mb-6"></div>
                          <div class="flex items-center gap-6">
                              <div class="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-2xl border border-white/5 backdrop-blur-sm shadow-xl">
                                  <div class="w-8 h-8 rounded-xl bg-blue-500/20 flex items-center justify-center">
                                      <i class="fa-solid fa-layer-group text-blue-400 text-xs"></i>
                                  </div>
                                  <div class="flex flex-col">
                                      <span class="text-[10px] text-slate-500 uppercase font-bold">进度</span>
                                      <span class="text-sm font-bold text-white">第 {{ currentExercise.current_sets }} <span class="text-slate-500 font-normal">/ {{ currentExercise.total_sets }} 组</span></span>
                                  </div>
                              </div>
                              <div class="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-2xl border border-white/5 backdrop-blur-sm shadow-xl">
                                  <div class="w-8 h-8 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                                      <i class="fa-solid fa-repeat text-emerald-400 text-xs"></i>
                                  </div>
                                  <div class="flex flex-col">
                                      <span class="text-[10px] text-slate-500 uppercase font-bold">目标</span>
                                      <span class="text-sm font-bold text-white">{{ currentExercise.reps_per_set || 12 }} <span class="text-slate-500 font-normal">次 / 组</span></span>
                                  </div>
                              </div>
                          </div>
                      </div>

                      <!-- 动作示例 GIF -->
                      <div v-if="currentExercise.gif_url && !cameraActive" class="relative w-full overflow-hidden mb-10 group rounded-3xl border border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] bg-slate-900/50 backdrop-blur-sm">
                          <!-- 背景虚化层 (填充比例差异，增加视觉深度) -->
                          <div class="absolute inset-0 scale-125 blur-3xl opacity-40 pointer-events-none">
                              <img :src="currentExercise.gif_url" class="w-full h-full object-cover" />
                          </div>
                          
                          <!-- 主图层 -->
                          <div class="relative w-full aspect-[3/4] sm:aspect-video flex items-center justify-center overflow-hidden">
                              <img :src="currentExercise.gif_url" class="max-w-full max-h-full object-contain relative z-10 drop-shadow-[0_10px_30px_rgba(0,0,0,0.5)]" />
                              
                              <!-- 底部渐变装饰 -->
                              <div class="absolute inset-0 bg-gradient-to-t from-slate-950/40 via-transparent to-transparent pointer-events-none"></div>
                              
                              <!-- 顶部标签 -->
                              <div class="absolute top-4 left-4 z-20">
                                  <div class="flex items-center gap-2 px-3.5 py-1.5 bg-blue-500/80 backdrop-blur-xl text-white rounded-xl text-[10px] font-bold uppercase tracking-widest shadow-xl border border-white/20">
                                      <span class="flex h-2 w-2 relative">
                                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                                          <span class="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
                                      </span>
                                      动作示例
                                  </div>
                              </div>

                              <!-- 装饰性光影 -->
                              <div class="absolute -inset-x-20 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent blur-sm"></div>
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
                      <div v-else class="relative w-56 h-56 mx-auto mb-12 flex items-center justify-center">
                          <!-- 背景阴影光效 -->
                          <div class="absolute inset-4 rounded-full blur-2xl opacity-20" :class="isCompleted ? 'bg-emerald-500' : 'bg-blue-500'"></div>
                          
                          <svg class="w-full h-full transform -rotate-90 relative z-10">
                              <defs>
                                  <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                      <stop offset="0%" stop-color="#3b82f6" />
                                      <stop offset="100%" stop-color="#60a5fa" />
                                  </linearGradient>
                                  <linearGradient id="successGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                      <stop offset="0%" stop-color="#10b981" />
                                      <stop offset="100%" stop-color="#34d399" />
                                  </linearGradient>
                              </defs>
                              <circle cx="112" cy="112" r="100" stroke="currentColor" stroke-width="6" fill="transparent" class="text-slate-700/80" />
                              <circle cx="112" cy="112" r="100" :stroke="isCompleted ? 'url(#successGradient)' : 'url(#progressGradient)'" stroke-width="10" fill="transparent" 
                                      :class="['progress-transition drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]']"
                                      :stroke-dasharray="2 * Math.PI * 100"
                                      :stroke-dashoffset="2 * Math.PI * 100 * (1 - currentPercent / 100)"
                                      stroke-linecap="round" />
                          </svg>
                          <div class="absolute inset-0 flex flex-col items-center justify-center z-20">
                              <div class="text-xs text-slate-500 font-bold uppercase tracking-widest mb-1">完成度</div>
                              <span class="text-5xl font-black text-white tracking-tighter">{{ isCompleted ? 'DONE' : currentPercent + '%' }}</span>
                              <button @click="incrementProgress" 
                                      class="mt-4 bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-1.5 rounded-2xl text-[10px] font-bold transition-all text-white backdrop-blur-md flex items-center gap-2 group">
                                  <i class="fa-solid fa-plus text-blue-400 group-hover:scale-125 transition-transform"></i>
                                  手动记录
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
                              class="relative w-full py-5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white rounded-2xl font-black transition-all shadow-[0_15px_30px_-5px_rgba(59,130,246,0.4)] hover:shadow-[0_20px_40px_-5px_rgba(59,130,246,0.5)] active:scale-[0.98] mb-10 flex items-center justify-center gap-3 overflow-hidden group">
                          <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                          <i class="fa-solid fa-camera-viewfinder text-xl"></i>
                          <span class="tracking-widest uppercase">开始 AI 辅助训练</span>
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
                          <div v-else class="space-y-2 max-h-40 overflow-y-auto pr-2 custom-scrollbar">
                              <div v-for="(log, logIndex) in exerciseHistory" :key="log.id" 
                                   @click="viewLogDetails(log)"
                                   class="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-white/5 hover:border-blue-500/50 transition-all cursor-pointer group">
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
                                      <div class="flex items-center gap-3 text-xs text-slate-300 mb-1">
                                          <span v-if="log.action_name" class="font-bold text-blue-400">{{ log.action_name }}</span>
                                          <span v-if="log.target_sets" class="flex items-center gap-1">
                                              <i class="fa-solid fa-layer-group text-[8px]"></i>
                                              {{ log.set_index || 1 }}/{{ log.target_sets }} 组
                                          </span>
                                          <span v-if="log.target_reps" class="flex items-center gap-1">
                                              <i class="fa-solid fa-repeat text-[8px]"></i>
                                              {{ log.reps_count }}/{{ log.target_reps }} 次
                                          </span>
                                      </div>
                                      <div v-if="log.ai_feedback" class="text-[10px] text-slate-500 line-clamp-1 italic">
                                          {{ log.ai_feedback }}
                                      </div>
                                  </div>
                                  <div v-if="log.ai_score !== null && log.ai_score !== undefined" 
                                       class="ml-3 flex flex-col items-end gap-2">
                                      <div class="px-2 py-1 rounded-lg bg-blue-500/20 border border-blue-500/30">
                                          <span class="text-xs font-bold text-blue-400">{{ Math.round(log.ai_score) }}</span>
                                      </div>
                                      <button @click="deleteLog(log.id, $event)" 
                                              class="w-6 h-6 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400/50 hover:text-red-400 flex items-center justify-center transition-all opacity-0 group-hover:opacity-100"
                                              title="删除记录">
                                          <i class="fa-solid fa-trash-can text-[10px]"></i>
                                      </button>
                                  </div>
                                  <div v-else class="ml-3 opacity-0 group-hover:opacity-100 transition-all">
                                      <button @click="deleteLog(log.id, $event)" 
                                              class="w-8 h-8 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400/50 hover:text-red-400 flex items-center justify-center transition-all"
                                              title="删除记录">
                                          <i class="fa-solid fa-trash-can text-xs"></i>
                                      </button>
                                  </div>
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
              <div class="max-w-md">
                  <div class="text-6xl mb-6">🏆</div>
                  <h2 class="text-3xl font-bold mb-4">太棒了！</h2>
                  <p class="text-slate-400 mb-8">您已完成今日所有训练项目。</p>

                  <!-- AI 评价区域 -->
                  <div v-if="evaluationResult" class="bg-slate-800/50 rounded-3xl p-6 mb-6 border border-white/10">
                      <div class="flex items-center gap-2 mb-4 text-xs font-bold text-slate-500 tracking-widest uppercase">
                          <i class="fa-solid fa-brain text-blue-400"></i> AI 训练评价
                      </div>

                      <!-- 评分 -->
                      <div class="text-center mb-4">
                          <div class="text-4xl font-black text-blue-400 mb-1">{{ evaluationResult.score }}/100</div>
                          <div class="text-xs text-slate-400 uppercase tracking-widest">综合评分</div>
                      </div>

                      <!-- 标准度 -->
                      <div class="flex items-center justify-center gap-2 mb-4">
                          <span :class="['px-3 py-1 rounded-full text-xs font-bold',
                            evaluationResult.is_standard ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400']">
                              {{ evaluationResult.is_standard ? '动作标准' : '需要改进' }}
                          </span>
                      </div>

                      <!-- 检测到的错误 -->
                      <div v-if="evaluationResult.detected_errors && evaluationResult.detected_errors.length > 0" class="mb-4">
                          <div class="text-xs text-slate-500 mb-2 uppercase tracking-widest">发现的问题</div>
                          <div class="space-y-2">
                              <div v-for="error in evaluationResult.detected_errors.slice(0, 3)" :key="error"
                                   class="flex items-start gap-2 text-xs text-amber-400 bg-amber-500/10 p-2 rounded-lg">
                                  <i class="fa-solid fa-triangle-exclamation mt-0.5"></i>
                                  <span>{{ error }}</span>
                              </div>
                          </div>
                      </div>

                      <!-- 改进建议 -->
                      <div v-if="evaluationResult.improvement_advice" class="mb-4">
                          <div class="text-xs text-slate-500 mb-2 uppercase tracking-widest">改进建议</div>
                          <div class="text-sm text-slate-300 bg-slate-700/50 p-3 rounded-lg leading-relaxed">
                              {{ evaluationResult.improvement_advice }}
                          </div>
                      </div>

                      <!-- 教练评价 -->
                      <div v-if="evaluationResult.coach_comment" class="text-sm text-slate-400 italic">
                          "{{ evaluationResult.coach_comment }}"
                      </div>
                  </div>

                  <!-- 视频保存状态 -->
                  <div v-if="savingVideo" class="mb-6">
                      <div class="w-full px-8 py-4 bg-blue-600/50 text-blue-300 rounded-2xl font-bold flex items-center justify-center gap-3">
                          <div class="w-5 h-5 border-2 border-blue-300 border-t-transparent rounded-full animate-spin"></div>
                          <span>正在保存训练视频...</span>
                      </div>
                  </div>

                  <!-- 已保存视频状态 -->
                  <div v-if="savedVideoInfo && !evaluationResult && !uploadingEvaluation && !savingVideo" class="mb-6">
                      <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4 mb-4">
                          <div class="flex items-center gap-3 text-emerald-400">
                              <i class="fa-solid fa-check-circle text-xl"></i>
                              <div>
                                  <div class="font-bold">训练视频已保存，等待分析结果...</div>
                                  <div class="text-sm text-emerald-300/80">{{ savedVideoInfo.filename }}</div>
                              </div>
                          </div>
                      </div>

                      <div class="w-full px-8 py-4 bg-slate-700/50 text-slate-400 rounded-2xl font-bold flex items-center justify-center gap-3">
                          <i class="fa-solid fa-clock-rotate-left"></i>
                          <span>等待 AI 分析任务启动...</span>
                      </div>
                  </div>

                  <!-- 上传中状态 (AI分析进度条) -->
                  <div v-if="uploadingEvaluation" class="mb-6">
                      <div class="bg-slate-800/50 rounded-3xl p-6 border border-white/10">
                          <div class="flex items-center justify-between mb-4">
                              <div class="flex items-center gap-2 text-xs font-bold text-blue-400 tracking-widest uppercase">
                                  <i class="fa-solid fa-brain animate-pulse"></i> AI 智能分析中
                              </div>
                              <span class="text-xs font-mono text-blue-400">{{ Math.round(evaluationProgress) }}%</span>
                          </div>
                          
                          <!-- 进度条背景 -->
                          <div class="w-full h-3 bg-slate-700 rounded-full overflow-hidden mb-4 shadow-inner">
                              <!-- 进度条填充 -->
                              <div class="h-full bg-gradient-to-r from-blue-600 to-blue-400 transition-all duration-500 ease-out"
                                   :style="{ width: `${evaluationProgress}%` }">
                              </div>
                          </div>
                          
                          <div class="text-[10px] text-slate-500 uppercase tracking-[0.2em] animate-pulse">
                              正在分析动作规范、力度与稳定性...
                          </div>
                      </div>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="flex gap-3">
                      <button @click="resetWorkout" class="flex-1 px-6 py-3 bg-slate-700/50 hover:bg-slate-600/50 text-white rounded-2xl font-bold transition-all">
                          重新开始
                      </button>
                      <button @click="showSummary = false" class="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-bold transition-all">
                          完成
                      </button>
                  </div>
              </div>
          </div>
      </transition>

      <!-- 训练记录详情弹窗 -->
      <transition name="fade">
          <div v-if="showLogDetails && selectedLog" class="fixed inset-0 z-[70] bg-slate-950/90 backdrop-blur-xl flex items-center justify-center p-6 text-white">
              <div class="max-w-md w-full bg-slate-900 rounded-[2.5rem] border border-white/10 overflow-hidden shadow-2xl">
                  <div class="p-8">
                      <div class="flex items-center justify-between mb-8">
                          <div>
                              <h2 class="text-2xl font-bold text-white mb-1">训练详情</h2>
                              <p class="text-xs text-slate-500 font-mono">{{ formatDate(selectedLog.start_time) }}</p>
                          </div>
                          <button @click="showLogDetails = false" class="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center transition-all">
                              <i class="fa-solid fa-xmark text-slate-400"></i>
                          </button>
                      </div>

                      <div class="space-y-6">
                          <!-- 基础信息 -->
                          <div class="grid grid-cols-2 gap-4">
                              <div class="bg-white/5 p-4 rounded-2xl border border-white/5">
                                  <div class="text-[10px] text-slate-500 uppercase font-bold mb-1">动作名称</div>
                                  <div class="text-sm font-bold text-white line-clamp-1">{{ selectedLog.action_name || '综合评价' }}</div>
                              </div>
                              <div class="bg-white/5 p-4 rounded-2xl border border-white/5">
                                  <div class="text-[10px] text-slate-500 uppercase font-bold mb-1">训练表现</div>
                                  <div class="text-sm font-bold text-blue-400">{{ selectedLog.ai_score ? Math.round(selectedLog.ai_score) + ' 分' : '未评分' }}</div>
                              </div>
                          </div>

                          <div class="grid grid-cols-2 gap-4" v-if="selectedLog.action_name !== '整体训练评价'">
                              <div class="bg-white/5 p-4 rounded-2xl border border-white/5">
                                  <div class="text-[10px] text-slate-500 uppercase font-bold mb-1">完成组数</div>
                                  <div class="text-sm font-bold text-white">第 {{ selectedLog.set_index || 1 }} / {{ selectedLog.target_sets || '--' }} 组</div>
                              </div>
                              <div class="bg-white/5 p-4 rounded-2xl border border-white/5">
                                  <div class="text-[10px] text-slate-500 uppercase font-bold mb-1">完成次数</div>
                                  <div class="text-sm font-bold text-emerald-400">{{ selectedLog.reps_count }} / {{ selectedLog.target_reps || '--' }} 次</div>
                              </div>
                          </div>

                          <!-- AI 反馈 -->
                          <div v-if="selectedLog.ai_feedback" class="bg-blue-500/5 border border-blue-500/10 rounded-3xl p-6">
                              <div class="flex items-center gap-2 mb-4 text-[10px] font-bold text-blue-400 tracking-widest uppercase">
                                  <i class="fa-solid fa-brain"></i> AI 教练反馈
                              </div>
                              <div class="text-sm text-slate-300 leading-relaxed whitespace-pre-line italic">
                                  {{ selectedLog.ai_feedback }}
                              </div>
                          </div>

                          <!-- 错误列表 (如果有) -->
                          <div v-if="selectedLog.data_snapshot && selectedLog.data_snapshot.detected_errors && selectedLog.data_snapshot.detected_errors.length" class="space-y-3">
                              <div class="text-[10px] font-bold text-slate-500 tracking-widest uppercase px-1">发现的问题</div>
                              <div class="space-y-2">
                                  <div v-for="error in selectedLog.data_snapshot.detected_errors" :key="error" class="flex items-start gap-3 p-3 rounded-2xl bg-amber-500/5 border border-amber-500/10 text-amber-400/90">
                                      <i class="fa-solid fa-triangle-exclamation text-xs mt-1"></i>
                                      <span class="text-xs leading-relaxed">{{ error }}</span>
                                  </div>
                              </div>
                          </div>
                      </div>

                      <button @click="showLogDetails = false" class="w-full mt-8 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-2xl font-bold transition-all">
                          我知道了
                      </button>
                  </div>
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
    const loadingSteps = ref(['同步历史记录', '准备今日训练']);
    const currentLoadingStep = ref(0);
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

    // AI 评价相关状态
    const evaluationResult = ref(null);  // AI评价结果
    const uploadingEvaluation = ref(false); // 上传评价状态
    const evaluationProgress = ref(0); // AI分析进度
    const savedVideoInfo = ref(null); // 已保存的视频信息
    const savingVideo = ref(false); // 保存视频状态

    // 训练历史详情
    const selectedLog = ref(null); // 当前选中的训练记录
    const showLogDetails = ref(false); // 是否显示训练记录详情

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

    // --- 完整训练视频录制状态 ---
    const trainingVideoRecorder = ref(null); // MediaRecorder实例
    const recordedChunks = ref([]); // 录制的视频数据块
    const isRecordingTraining = ref(false); // 是否正在录制完整训练视频
    const isTrainingCompleted = ref(false); // 训练是否完成（用于判断是否应该保存和分析视频）

    // 动作类型映射
    const getExerciseType = (exercise) => {
      if (!exercise) return 'general';
      
      // 优先使用后端返回的 category
      if (exercise.category) return exercise.category;
      
      const name = exercise.name || '';
      if (name.includes('深蹲')) return 'squat';
      if (name.includes('弯举')) return 'curl';
      if (name.includes('推肩') || name.includes('卧推')) return 'press';
      return 'elbow_dominant'; // 默认使用新分类中的一种
    };

    const getPoseStateText = () => {
      const type = getExerciseType(currentExercise.value);
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
        
        // 重置训练完成状态
        isTrainingCompleted.value = false;
        
        // 记录开始时间和重置时长
        startTime.value = new Date();
        duration.value = 0;
        
        // 创建训练日志
        await createWorkoutLog();

        // 开始录制完整训练视频
        startTrainingVideoRecording(s);
        
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

    const startTrainingVideoRecording = (stream) => {
      try {
        recordedChunks.value = [];
        const options = {
          mimeType: 'video/webm;codecs=vp9'
        };

        // 检查是否支持该格式，如果不支持则使用默认格式
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          options.mimeType = 'video/webm;codecs=vp8';
          if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = ''; // 使用浏览器默认格式
          }
        }

        trainingVideoRecorder.value = new MediaRecorder(stream, options);
        trainingVideoRecorder.value.ondataavailable = (event) => {
          if (event.data.size > 0) {
            recordedChunks.value.push(event.data);
          }
        };

        trainingVideoRecorder.value.onstop = async () => {
          // 录制停止时，只有完成的训练才保存视频
          if (isTrainingCompleted.value) {
            await saveRecordedTrainingVideo();
          } else {
            // 如果是中断的训练，清空录制的数据，不保存
            recordedChunks.value = [];
            console.log('训练已中断，不保存视频');
          }
        };

        trainingVideoRecorder.value.start(1000); // 每秒收集一次数据
        isRecordingTraining.value = true;
        console.log('开始录制完整训练视频');
      } catch (err) {
        console.error('开始录制训练视频失败:', err);
      }
    };

    const stopTrainingVideoRecording = () => {
      if (trainingVideoRecorder.value && isRecordingTraining.value) {
        trainingVideoRecorder.value.stop();
        isRecordingTraining.value = false;
        console.log('停止录制完整训练视频');
      }
    };

    const saveRecordedTrainingVideo = async () => {
      // 只有完成的训练才保存视频
      if (!isTrainingCompleted.value) {
        console.log('训练未完成，不保存视频');
        recordedChunks.value = []; // 清空数据
        return;
      }

      if (recordedChunks.value.length === 0) {
        console.log('没有录制的视频数据');
        return;
      }

      try {
        const blob = new Blob(recordedChunks.value, { type: 'video/webm' });
        const formData = new FormData();
        formData.append('video', blob, `training_${Date.now()}.webm`);
        formData.append('plan_id', currentWorkoutId.value || '');
        formData.append('session_id', Date.now().toString());

        savingVideo.value = true;
        const response = await axios.post('/api/save-training-video/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.data.success) {
          savedVideoInfo.value = response.data.data;
          console.log('完整训练视频已保存:', savedVideoInfo.value);

          // 视频保存成功后，自动开始AI分析
          await autoEvaluateTraining();
        } else {
          console.error('保存训练视频失败:', response.data.error);
        }
      } catch (err) {
        console.error('保存训练视频请求失败:', err);
      } finally {
        savingVideo.value = false;
        recordedChunks.value = []; // 清空录制的数据
      }
    };

    const stopCamera = async (status = 'interrupted') => {
      // 如果 status 是事件对象（点击关闭按钮时），则默认为 'interrupted'
      const finalStatus = typeof status === 'string' ? status : 'interrupted';

      // 设置训练完成状态
      isTrainingCompleted.value = (finalStatus === 'completed');
      
      // 停止训练视频录制（只在完成训练时保存）
      if (finalStatus === 'completed') {
        stopTrainingVideoRecording();
      } else {
        // 如果是中断的训练，直接停止录制但不保存
        if (trainingVideoRecorder.value && isRecordingTraining.value) {
          trainingVideoRecorder.value.stop();
          isRecordingTraining.value = false;
          recordedChunks.value = []; // 清空数据
          console.log('训练已中断，停止录制并清空数据');
        }
      }
      
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
        const response = await axios.post('/api/logs/', {
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
        await axios.patch(`/api/logs/${currentLogId.value}/`, {
          reps_count: reps.value,
          duration: duration.value,
          status: finalStatus,
          exercise_id: currentExercise.value.id,
          target_reps: currentExercise.value.reps_per_set || 12,
          target_sets: currentExercise.value.total_sets
        });
        console.log('训练记录已更新:', currentLogId.value, '状态:', finalStatus);
        currentLogId.value = null;
        await fetchExerciseHistory(); // 重新加载，确保最新的完成记录可见
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

        const response = await axios.post('/api/analyze-pose/', {
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
      loadingSteps.value = ['同步历史记录', '初始化环境'];
      currentLoadingStep.value = 0;
      try {
        await fetchHistory();
        currentLoadingStep.value = 1;
        await new Promise(resolve => setTimeout(resolve, 600));
      } catch (e) {
        console.error("加载失败", e);
      } finally {
        loading.value = false;
      }
    };

    const fetchHistory = async () => {
      try {
        const response = await axios.get('/api/plans/');
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
        const plan = history.value.find(p => p.id === currentWorkoutId.value);
        const planTitle = plan ? plan.title : null;

        const response = await axios.get('/api/logs/');
        const allLogs = Array.isArray(response.data) ? response.data : [];
        
        // 过滤逻辑：属于当前动作的记录 OR (属于当前计划的整体评价)
        exerciseHistory.value = allLogs.filter(log => {
          const isCurrentExercise = (currentExercise.value.id && log.exercise_id === currentExercise.value.id) || 
                                   (log.action_name === currentExercise.value.name);
          const isOverallEvaluation = log.action_name === "整体训练评价" && planTitle && log.plan_title === planTitle;
          
          return isCurrentExercise || isOverallEvaluation;
        }).slice(0, 10);
      } catch (e) {
        console.error("获取训练历史失败", e);
        exerciseHistory.value = [];
      }
    };

    const viewLogDetails = (log) => {
      selectedLog.value = log;
      showLogDetails.value = true;
    };

    const saveCurrentWorkout = async (title = '') => {
      if (exercises.value.length === 0) return;
      
      const workoutTitle = title || `训练计划 ${new Date().toLocaleDateString()}`;
      try {
        const response = await axios.post('/api/plans/', {
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
        await axios.delete(`/api/plans/${id}/`);
        if (currentWorkoutId.value === id) {
          currentWorkoutId.value = null;
        }
        await fetchHistory();
      } catch (e) {
        console.error("删除失败", e);
      }
    };

    const deleteLog = async (id, event) => {
      // 阻止冒泡，防止触发 viewLogDetails
      if (event) event.stopPropagation();
      
      if (!confirm('确定删除这条训练记录吗？')) return;
      
      try {
        const response = await axios.delete(`/api/logs/${id}/`);
        // 删除成功后刷新列表
        await fetchExerciseHistory();
      } catch (e) {
        console.error("删除记录失败", e);
        // 即使删除失败，也尝试刷新列表（可能是记录已经不存在）
        try {
          await fetchExerciseHistory();
        } catch (refreshError) {
          console.error("刷新列表失败", refreshError);
        }
        // 检查是否是404错误（记录不存在）
        if (e.response && e.response.status === 404) {
          // 记录不存在，忽略错误，直接刷新列表
          return;
        }
        alert('删除失败: ' + (e.response?.data?.error || e.message || '未知错误'));
      }
    };

    const startEdit = (item) => {
      editingId.value = item.id;
      editingTitle.value = item.title || '';
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
      const titleToSave = (editingTitle.value || '').trim();
      if (!titleToSave) {
        alert('计划名称不能为空');
        return;
      }
      try {
        await axios.patch(`/api/plans/${id}/`, {
          title: titleToSave
        });
        const item = history.value.find(h => h.id === id);
        if (item) {
          item.title = titleToSave;
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
        await axios.patch(`/api/plans/${currentWorkoutId.value}/`, {
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
      const file = event && event.target ? event.target.files[0] : null;
      if (!file) return;

      const formData = new FormData();
      formData.append('video', file);

      loading.value = true;
      loadingSteps.value = ['上传视频文件', 'AI 动作分析', '生成演示片段', '同步训练计划'];
      currentLoadingStep.value = 0;

      try {
        const response = await axios.post('/api/analyze-video/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            if (percentCompleted >= 100) {
              currentLoadingStep.value = 1;
            }
          }
        });

        // 由于后端分析和GIF生成是在同一个接口，我们在这里直接跳到完成
        currentLoadingStep.value = 2;

        if (response.data.success) {
          currentLoadingStep.value = 3;
          const result = response.data.data;
          exercises.value = result.exercises || [];
          currentIndex.value = 0;
          showSummary.value = false;
          
          // 自动保存到历史，使用 AI 生成的标题
          const aiTitle = result.title || `AI分析 - ${new Date().toLocaleDateString()}`;
          await saveCurrentWorkout(aiTitle);
          
          // 留出时间让用户看清"同步完成"
          await new Promise(resolve => setTimeout(resolve, 800));
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

    const autoEvaluateTraining = async () => {
      // 只有完成的训练才提交AI分析
      if (!isTrainingCompleted.value) {
        console.log('训练未完成，不提交AI分析');
        return;
      }

      if (!savedVideoInfo.value) {
        console.log('没有已保存的视频信息，跳过自动评价');
        return;
      }

      try {
        uploadingEvaluation.value = true;
        evaluationResult.value = null;

        const formData = new FormData();

        // 使用已保存的视频路径
        formData.append('video_path', savedVideoInfo.value.video_path);

        // 收集当前训练计划的所有动作信息，用于AI评价
        const workoutPlan = exercises.value.map(exercise => ({
          id: exercise.id,
          name: exercise.name,
          tips: exercise.tips || '',
          total_sets: exercise.total_sets,
          reps_per_set: exercise.reps_per_set
        }));

        formData.append('workout_plan', JSON.stringify(workoutPlan));
        formData.append('plan_id', currentWorkoutId.value || '');
        formData.append('training_status', 'completed'); // 明确传递训练状态

        console.log('开始自动AI分析训练视频...');

        // 发送到评价API
        const response = await axios.post('/api/evaluate-training-video/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.data.success) {
          evaluationResult.value = response.data.data;
          console.log('AI评价完成:', evaluationResult.value);
        } else {
          console.error('AI评价失败:', response.data.error);
        }
      } catch (err) {
        console.error('自动AI评价失败:', err);
      } finally {
        uploadingEvaluation.value = false;
      }
    };

    const autoSaveTrainingVideo = async () => {
      // 这个函数现在不需要额外操作，因为视频录制会在stopCamera中处理
      console.log('训练完成，视频录制将在摄像头关闭时自动保存');
    };

    const handleTrainingVideoUpload = async (event) => {
      const file = event && event.target ? event.target.files[0] : null;
      if (!file && !savedVideoInfo.value) return;

      uploadingEvaluation.value = true;
      evaluationResult.value = null;

      try {
        const formData = new FormData();

        // 如果有已保存的视频，使用已保存的视频路径；否则使用新上传的文件
        if (savedVideoInfo.value) {
          formData.append('video_path', savedVideoInfo.value.video_path);
        } else {
          formData.append('video', file);
        }

        // 收集当前训练计划的所有动作信息，用于AI评价
        const workoutPlan = exercises.value.map(exercise => ({
          id: exercise.id,
          name: exercise.name,
          tips: exercise.tips || '',
          total_sets: exercise.total_sets,
          reps_per_set: exercise.reps_per_set
        }));

        formData.append('workout_plan', JSON.stringify(workoutPlan));
        formData.append('plan_id', currentWorkoutId.value || '');

        // 发送到评价API
        const response = await axios.post('/api/evaluate-training-video/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.data.success) {
          evaluationResult.value = response.data.data;
        } else {
          alert('评价失败: ' + (response.data.error || '未知错误'));
        }
      } catch (err) {
        console.error('评价失败:', err);
        alert('AI评价失败，请稍后重试');
      } finally {
        uploadingEvaluation.value = false;
        // 清空 input 方便下次上传同一文件
        if (event && event.target) {
          event.target.value = '';
        }
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
      if (Array.isArray(tips)) return tips.filter(t => t && typeof t === 'string' && t.trim());
      if (typeof tips !== 'string') return [];
      return tips.split(/[；;。]/).filter(t => t && t.trim());
    };

    const resetWorkout = () => {
      exercises.value.forEach(e => e.current_sets = 0);
      currentIndex.value = 0;
      showSummary.value = false;
      evaluationResult.value = null;
      uploadingEvaluation.value = false;
      evaluationProgress.value = 0;
      savedVideoInfo.value = null;
      savingVideo.value = false;
      recordedChunks.value = [];
      isTrainingCompleted.value = false;
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
      loading, loadingSteps, currentLoadingStep, syncing, autoJumping, showSummary, transitionName,
      history, showHistory, exerciseHistory,
      cameraActive, analyzing, error, feedback, annotatedImage, reps, poseState, videoElement,
      startCamera, stopCamera, getPoseStateText,
      incrementProgress, next, prev, parseTips, resetWorkout,
      handleTouchStart, handleTouchEnd, handleVideoUpload,
      fetchHistory, saveCurrentWorkout, loadWorkout, deleteHistoryItem, deleteLog, formatDate,
      editingId, editingTitle, startEdit, cancelEdit, saveEdit,
      evaluationResult, uploadingEvaluation, evaluationProgress, handleTrainingVideoUpload,
      savedVideoInfo, savingVideo, isRecordingTraining, autoEvaluateTraining,
      selectedLog, showLogDetails, viewLogDetails
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

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
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
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(45, 212, 191, 0.9) transparent;
}
 .custom-scrollbar::-webkit-scrollbar {
  width: 6px;
 }
 .custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 999px;
 }
 .custom-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(14, 165, 233, 0.85), rgba(59, 130, 246, 0.85));
  border-radius: 999px;
  border: 1px solid rgba(15, 23, 42, 0.8);
 }
 .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(34, 211, 238, 1), rgba(96, 165, 250, 1));
 }
 </style>

