<template>
  <div class="w-full max-w-2xl h-full max-h-[900px] flex flex-col p-6 relative overflow-hidden">
    <div class="glass-card p-8 rounded-[2.5rem] shadow-2xl overflow-y-auto">
      <header class="mb-8">
        <router-link to="/" class="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-4 block hover:underline">
          <i class="fa-solid fa-arrow-left mr-2"></i> 返回主页
        </router-link>
        <h1 class="text-4xl font-bold text-white mb-2 leading-tight">AI动作指导</h1>
        <p class="text-slate-400 text-sm">打开摄像头，AI将实时分析您的动作并提供指导</p>
      </header>
      
      <div class="mb-8">
        <div class="relative w-full aspect-video bg-slate-900 rounded-3xl overflow-hidden border border-white/10">
          <video
            ref="videoElement"
            autoplay
            playsinline
            class="w-full h-full object-cover"
          ></video>
          <canvas
            ref="canvasElement"
            class="absolute inset-0 w-full h-full pointer-events-none"
          ></canvas>
          <div v-if="!cameraActive" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-sm">
            <i class="fa-solid fa-camera text-4xl text-slate-700 mb-4"></i>
            <p class="text-slate-500 text-sm">点击下方按钮启动摄像头</p>
          </div>
        </div>
        
        <div class="flex gap-4 mt-6">
          <button
            v-if="!cameraActive"
            @click="startCamera"
            class="flex-1 py-4 bg-blue-600 hover:bg-blue-500 rounded-2xl font-bold text-white transition-all shadow-lg shadow-blue-500/20"
          >
            <i class="fa-solid fa-video mr-2"></i> 启动摄像头
          </button>
          <button
            v-else
            @click="stopCamera"
            class="flex-1 py-4 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-2xl font-bold transition-all border border-red-500/20"
          >
            <i class="fa-solid fa-stop mr-2"></i> 停止摄像头
          </button>
          <button
            v-if="cameraActive"
            @click="captureAndAnalyze"
            :disabled="analyzing"
            class="flex-1 py-4 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 rounded-2xl font-bold text-white transition-all shadow-lg shadow-emerald-500/20"
          >
            {{ analyzing ? '分析中...' : '📸 分析动作' }}
          </button>
        </div>
      </div>

      <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-2xl mb-6 text-sm">
        {{ error }}
      </div>

      <div v-if="feedback.length > 0" class="space-y-6">
        <h3 class="text-xs font-bold text-slate-500 tracking-widest uppercase">AI指导反馈</h3>
        <div class="space-y-3">
          <div
            v-for="(item, index) in feedback"
            :key="index"
            :class="['flex items-center gap-4 p-4 rounded-2xl border transition-all',
                     item.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 
                     item.type === 'warning' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' : 
                     'bg-blue-500/10 border-blue-500/20 text-blue-400']"
          >
            <i :class="['fa-solid', 
                        item.type === 'success' ? 'fa-check-circle' : 
                        item.type === 'warning' ? 'fa-exclamation-triangle' : 
                        'fa-info-circle']"></i>
            <span class="text-sm font-medium">{{ item.message }}</span>
          </div>
        </div>
      </div>

      <div v-if="annotatedImage" class="mt-8 space-y-4">
        <h3 class="text-xs font-bold text-slate-500 tracking-widest uppercase">姿态标注图</h3>
        <img :src="annotatedImage" alt="Annotated Pose" class="w-full rounded-3xl border border-white/10" />
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
      analysisInterval: null
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
    async startCamera() {
      try {
        this.error = null
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          }
        })
        
        this.stream = stream
        this.cameraActive = true
        
        if (this.$refs.videoElement) {
          this.$refs.videoElement.srcObject = stream
        }
      } catch (err) {
        this.error = '无法访问摄像头，请检查权限设置'
        console.error('Camera error:', err)
      }
    },
    
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop())
        this.stream = null
      }
      this.cameraActive = false
      this.feedback = []
      this.annotatedImage = null
      
      if (this.analysisInterval) {
        clearInterval(this.analysisInterval)
        this.analysisInterval = null
      }
    },
    
    async captureAndAnalyze() {
      if (!this.cameraActive || !this.$refs.videoElement) {
        return
      }

      this.analyzing = true
      this.error = null

      try {
        const canvas = this.$refs.canvasElement
        const video = this.$refs.videoElement
        
        if (!canvas || !video) {
          throw new Error('无法访问视频元素')
        }

        canvas.width = video.videoWidth
        canvas.height = video.videoHeight

        const ctx = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        const imageData = canvas.toDataURL('image/jpeg', 0.8)

        const response = await axios.post('http://localhost:8000/api/analyze-pose/', {
          image: imageData
        })

        if (response.data.success) {
          this.feedback = response.data.data.feedback || []
          this.annotatedImage = response.data.data.annotated_image
        } else {
          this.error = response.data.error || '分析失败'
          this.feedback = []
        }
      } catch (err) {
        this.error = err.response?.data?.error || '分析失败，请检查后端服务'
        console.error('Analysis error:', err)
        this.feedback = []
      } finally {
        this.analyzing = false
      }
    },
    
    cleanup() {
      this.stopCamera()
    }
  }
}
</script>

<style scoped>
.glass-card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

