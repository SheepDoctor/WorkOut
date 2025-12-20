<template>
  <div class="w-full max-w-4xl h-full flex flex-col p-6 relative overflow-hidden mx-auto">
    <div class="glass-card p-8 rounded-[2.5rem] shadow-2xl overflow-y-auto">
      <header class="mb-6 flex justify-between items-center">
        <div>
          <router-link to="/" class="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-2 block hover:underline">
            <i class="fa-solid fa-arrow-left mr-2"></i> 返回主页
          </router-link>
          <h1 class="text-3xl font-bold text-white leading-tight">AI 智能训练助手</h1>
        </div>
        
        <!-- 训练状态面板 -->
        <div v-if="cameraActive" class="flex gap-4">
            <div class="bg-slate-800/50 p-3 rounded-xl border border-white/10 text-center min-w-[80px]">
                <div class="text-xs text-slate-400 uppercase tracking-wider">REPS</div>
                <div class="text-2xl font-bold text-emerald-400">{{ reps }} <span class="text-xs text-slate-500">/ {{ targetReps }}</span></div>
            </div>
            <div class="bg-slate-800/50 p-3 rounded-xl border border-white/10 text-center min-w-[80px]">
                <div class="text-xs text-slate-400 uppercase tracking-wider">SETS</div>
                <div class="text-2xl font-bold text-blue-400">{{ sets }} <span class="text-xs text-slate-500">/ {{ targetSets }}</span></div>
            </div>
        </div>
      </header>

      <!-- 设置区域 (仅在摄像头未开启时显示) -->
      <div v-if="!cameraActive && !workoutComplete" class="mb-8 bg-slate-800/30 p-6 rounded-2xl border border-white/5">
        <h3 class="text-lg font-bold text-white mb-4">训练计划设置</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
                <label class="block text-slate-400 text-sm mb-2">选择动作</label>
                <select v-model="exerciseType" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-blue-500 outline-none">
                    <option value="squat">深蹲 (Squat)</option>
                    <option value="curl">哑铃弯举 (Dumbbell Curl)</option>
                    <option value="press">哑铃推肩 (Shoulder Press)</option>
                </select>
            </div>
            <div>
                <label class="block text-slate-400 text-sm mb-2">每组次数 (Reps)</label>
                <input type="number" v-model.number="targetReps" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-blue-500 outline-none" min="1" max="100">
            </div>
            <div>
                <label class="block text-slate-400 text-sm mb-2">目标组数 (Sets)</label>
                <input type="number" v-model.number="targetSets" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:border-blue-500 outline-none" min="1" max="10">
            </div>
        </div>
      </div>
      
      <!-- 视频区域 -->
      <div class="mb-6 relative">
        <div class="relative w-full aspect-video bg-slate-900 rounded-3xl overflow-hidden border border-white/10 shadow-inner">
          <video
            ref="videoElement"
            autoplay
            playsinline
            class="w-full h-full object-cover"
            :class="{ 'opacity-50': workoutComplete }"
          ></video>
          <!-- 结果叠加层 -->
          <img 
            v-if="annotatedImage && cameraActive && !workoutComplete" 
            :src="annotatedImage" 
            class="absolute inset-0 w-full h-full object-cover"
          />
          
          <!-- 状态指示器 -->
          <div v-if="cameraActive && !workoutComplete" class="absolute top-4 left-4">
             <div :class="['px-4 py-2 rounded-full font-bold text-sm shadow-lg backdrop-blur-md', 
                poseState === 'UP' ? 'bg-blue-500/80 text-white' : 
                poseState === 'DOWN' ? 'bg-amber-500/80 text-white' : 
                'bg-slate-700/80 text-slate-300']">
                {{ getPoseStateText() }}
             </div>
          </div>

          <div v-if="!cameraActive && !workoutComplete" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-sm z-10">
            <i class="fa-solid fa-camera text-5xl text-slate-600 mb-4"></i>
            <p class="text-slate-500">准备好后点击启动</p>
          </div>

          <!-- 训练完成提示 -->
          <div v-if="workoutComplete" class="absolute inset-0 flex flex-col items-center justify-center bg-emerald-900/90 backdrop-blur-md z-20">
            <i class="fa-solid fa-trophy text-6xl text-yellow-400 mb-4 animate-bounce"></i>
            <h2 class="text-3xl font-bold text-white mb-2">训练完成!</h2>
            <p class="text-emerald-200 mb-6">恭喜你完成了 {{ targetSets }} 组训练</p>
            <button @click="resetWorkout" class="px-8 py-3 bg-white text-emerald-700 rounded-full font-bold hover:bg-emerald-50 transition-colors shadow-lg">
                开始新训练
            </button>
          </div>
        </div>
        
        <!-- 控制按钮 -->
        <div class="flex gap-4 mt-6">
          <button
            v-if="!cameraActive"
            @click="startCamera"
            class="flex-1 py-4 bg-blue-600 hover:bg-blue-500 rounded-2xl font-bold text-white transition-all shadow-lg shadow-blue-500/20 text-lg"
          >
            <i class="fa-solid fa-play mr-2"></i> 开始训练
          </button>
          <button
            v-else
            @click="stopCamera"
            class="flex-1 py-4 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-2xl font-bold transition-all border border-red-500/20"
          >
            <i class="fa-solid fa-stop mr-2"></i> 结束训练
          </button>
        </div>
      </div>

      <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-2xl mb-6 text-sm flex items-center">
        <i class="fa-solid fa-circle-exclamation mr-2"></i> {{ error }}
      </div>

      <!-- AI 反馈列表 -->
      <div v-if="feedback.length > 0 && cameraActive" class="space-y-3">
        <div
            v-for="(item, index) in feedback"
            :key="index"
            :class="['flex items-center gap-3 p-3 rounded-xl border transition-all text-sm',
                        item.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 
                        item.type === 'warning' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' : 
                        'bg-blue-500/10 border-blue-500/20 text-blue-400']"
            >
            <i :class="['fa-solid', 
                        item.type === 'success' ? 'fa-check-circle' : 
                        item.type === 'warning' ? 'fa-exclamation-triangle' : 
                        'fa-info-circle']"></i>
            <span>{{ item.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PoseAnalyzer',
  data() {
    return {
      cameraActive: false,
      analyzing: false,
      error: null,
      feedback: [],
      annotatedImage: null,
      stream: null,
      analysisInterval: null,
      
      // 训练设置
      exerciseType: 'squat',
      targetReps: 5,
      targetSets: 3,
      
      // 训练状态
      reps: 0,
      sets: 0,
      poseState: 'UNKNOWN',
      lastPoseState: 'UNKNOWN',
      workoutComplete: false,
      
      // 计数逻辑辅助
      isDown: false // 用于深蹲/弯举的中间状态标记
    }
  },
  mounted() {
    this.$nextTick(() => {
      window.addEventListener('beforeunload', this.cleanup)
    })
  },
  beforeUnmount() {
    this.cleanup()
    window.removeEventListener('beforeunload', this.cleanup)
  },
  methods: {
    getPoseStateText() {
        const map = {
            'UP': this.exerciseType === 'squat' ? '站立 (UP)' : (this.exerciseType === 'press' ? '推起 (UP)' : '举起 (UP)'),
            'DOWN': this.exerciseType === 'squat' ? '下蹲 (DOWN)' : '放下 (DOWN)',
            'TRANSITION': '动作中...',
            'UNKNOWN': '准备中'
        }
        return map[this.poseState] || this.poseState
    },
    
    resetWorkout() {
        this.workoutComplete = false
        this.reps = 0
        this.sets = 0
        this.poseState = 'UNKNOWN'
        this.lastPoseState = 'UNKNOWN'
        this.isDown = false
        this.annotatedImage = null
        this.feedback = []
    },

    async startCamera() {
      if (this.workoutComplete) this.resetWorkout()
      
      try {
        this.error = null
        // 降低分辨率以提高传输速度
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
          }
        })
        
        this.stream = stream
        this.cameraActive = true
        
        if (this.$refs.videoElement) {
          this.$refs.videoElement.srcObject = stream
        }
        
        // 启动分析循环
        this.analyzeLoop()
        
      } catch (err) {
        this.error = '无法访问摄像头，请检查权限设置'
        console.error('Camera error:', err)
      }
    },
    
    async analyzeLoop() {
        if (!this.cameraActive || this.workoutComplete) return

        if (!this.analyzing) {
            await this.captureAndAnalyze()
        }
        
        // 使用 requestAnimationFrame 尽可能快地请求下一帧，
        // 但受到 captureAndAnalyze 的 await 限制，实际上是串行的
        requestAnimationFrame(() => this.analyzeLoop())
    },
    
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop())
        this.stream = null
      }
      this.cameraActive = false
      // loop 会在 cameraActive 变为 false 时自动停止
    },
    
    async captureAndAnalyze() {
      if (!this.cameraActive || !this.$refs.videoElement) return

      this.analyzing = true
      // 不要每次清除 feedback，避免闪烁
      // this.error = null 

      try {
        const canvas = document.createElement('canvas') // 使用离屏 canvas
        const video = this.$refs.videoElement
        
        if (video.readyState !== 4) { // 确保视频已就绪
            this.analyzing = false
            return
        }

        canvas.width = 480 // 限制上传宽度为 480px，足够用于姿态检测
        canvas.height = video.videoHeight * (480 / video.videoWidth)
        
        // 绘制并压缩
        const ctx = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        const imageData = canvas.toDataURL('image/jpeg', 0.5) // 进一步降低质量以加速传输

        const response = await axios.post('http://localhost:8000/api/analyze-pose/', {
          image: imageData,
          exercise_type: this.exerciseType
        })

        if (response.data.success) {
          const data = response.data.data
          this.feedback = data.feedback || []
          this.annotatedImage = data.annotated_image
          
          // 更新姿态状态
          this.updateWorkoutState(data.pose_state, data.pose_angle)
          
        } else {
           // 忽略单次失败，避免刷屏
           console.warn('Analysis failed:', response.data.error)
        }
      } catch (err) {
        console.error('Analysis error:', err)
        // 网络错误通常是暂时的，不要停止，只是记录
      } finally {
        this.analyzing = false
      }
    },
    
    updateWorkoutState(currentOriginalState, angle) {
        // 简单的防抖或状态平滑可以在这里做，目前直接使用后端状态
        const currentState = currentOriginalState
        
        if (this.exerciseType === 'squat') {
            // 深蹲逻辑: UP -> DOWN (标记) -> UP (计数)
            if (currentState === 'DOWN') {
                this.isDown = true
            } else if (currentState === 'UP' && this.isDown) {
                this.incrementReps()
                this.isDown = false // 重置
            }
        } else if (this.exerciseType === 'curl' || this.exerciseType === 'press') {
            // 弯举/推肩逻辑: DOWN -> UP (标记) -> DOWN (计数)
            // detect_curl/press 返回 UP 是举起/推起，DOWN 是放下
            if (currentState === 'UP') {
                this.isDown = true // 复用变量名，这里代表"动作高点"
            } else if (currentState === 'DOWN' && this.isDown) {
                this.incrementReps()
                this.isDown = false
            }
        }
        
        this.poseState = currentState
        this.lastPoseState = currentState
    },
    
    incrementReps() {
        this.reps++
        // 播放提示音 (可选)
        // new Audio('/beep.mp3').play().catch(e => {})
        
        if (this.reps >= this.targetReps) {
            this.completeSet()
        }
    },
    
    completeSet() {
        this.sets++
        this.reps = 0
        this.isDown = false
        
        if (this.sets >= this.targetSets) {
            this.finishWorkout()
        } else {
             // 组间休息提示
             this.feedback = [{ type: 'success', message: `第 ${this.sets} 组完成！休息一下继续。` }]
        }
    },
    
    finishWorkout() {
        this.workoutComplete = true
        this.stopCamera()
    },
    
    cleanup() {
      this.stopCamera()
    }
  }
}
</script>

<style scoped>
.glass-card {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
