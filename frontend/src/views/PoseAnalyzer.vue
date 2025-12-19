<template>
  <div class="pose-analyzer">
    <div class="card">
      <h2 class="card-title">🤖 AI动作指导</h2>
      <p class="card-subtitle">打开摄像头，AI将实时分析您的动作并提供指导</p>
      
      <div class="camera-section">
        <div class="video-container">
          <video
            ref="videoElement"
            autoplay
            playsinline
            class="video-preview"
          ></video>
          <canvas
            ref="canvasElement"
            class="canvas-overlay"
          ></canvas>
          <div v-if="!cameraActive" class="camera-placeholder">
            <p>📷 点击下方按钮启动摄像头</p>
          </div>
        </div>
        
        <div class="controls">
          <button
            v-if="!cameraActive"
            @click="startCamera"
            class="control-btn start-btn"
          >
            🎥 启动摄像头
          </button>
          <button
            v-else
            @click="stopCamera"
            class="control-btn stop-btn"
          >
            ⏹️ 停止摄像头
          </button>
          <button
            v-if="cameraActive"
            @click="captureAndAnalyze"
            :disabled="analyzing"
            class="control-btn analyze-btn"
          >
            {{ analyzing ? '分析中...' : '📸 分析当前动作' }}
          </button>
        </div>
      </div>

      <div v-if="error" class="error-message">
        ❌ {{ error }}
      </div>

      <div v-if="feedback.length > 0" class="feedback-section">
        <h3 class="feedback-title">AI指导反馈</h3>
        <div class="feedback-list">
          <div
            v-for="(item, index) in feedback"
            :key="index"
            class="feedback-item"
            :class="item.type"
          >
            <span class="feedback-icon">
              {{ item.type === 'success' ? '✅' : item.type === 'warning' ? '⚠️' : 'ℹ️' }}
            </span>
            <span class="feedback-message">{{ item.message }}</span>
          </div>
        </div>
      </div>

      <div v-if="annotatedImage" class="annotated-image-section">
        <h3 class="feedback-title">姿态标注图</h3>
        <img :src="annotatedImage" alt="Annotated Pose" class="annotated-image" />
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
    // 组件卸载时清理
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

        // 设置canvas尺寸
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight

        // 将视频帧绘制到canvas
        const ctx = canvas.getContext('2d')
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        // 将canvas转换为base64
        const imageData = canvas.toDataURL('image/jpeg', 0.8)

        // 发送到后端分析
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
.pose-analyzer {
  min-height: calc(100vh - 200px);
}

.card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.card-subtitle {
  color: #666;
  margin-bottom: 2rem;
}

.camera-section {
  margin-bottom: 2rem;
}

.video-container {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto 1.5rem;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
}

.video-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.canvas-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.camera-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  text-align: center;
  font-size: 1.2rem;
}

.controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.control-btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.start-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stop-btn {
  background: #dc3545;
  color: white;
}

.analyze-btn {
  background: #28a745;
  color: white;
}

.control-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.control-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border-left: 4px solid #c33;
}

.feedback-section {
  margin-top: 2rem;
}

.feedback-title {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.feedback-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f8f9fa;
}

.feedback-item.success {
  background: #d4edda;
  border-left: 4px solid #28a745;
}

.feedback-item.warning {
  background: #fff3cd;
  border-left: 4px solid #ffc107;
}

.feedback-item.info {
  background: #d1ecf1;
  border-left: 4px solid #17a2b8;
}

.feedback-icon {
  font-size: 1.5rem;
}

.feedback-message {
  color: #333;
  font-weight: 500;
}

.annotated-image-section {
  margin-top: 2rem;
}

.annotated-image {
  width: 100%;
  max-width: 800px;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}
</style>

