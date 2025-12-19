<template>
  <div class="douyin-analyzer">
    <div class="card">
      <h2 class="card-title">📱 抖音链接分析</h2>
      <p class="card-subtitle">输入抖音视频或图文链接，获取详细信息</p>
      
      <div class="input-section">
        <input
          v-model="douyinUrl"
          type="text"
          placeholder="请输入抖音链接，例如：https://www.douyin.com/video/..."
          class="url-input"
        />
        <button @click="analyzeUrl" :disabled="loading" class="analyze-btn">
          {{ loading ? '分析中...' : '分析链接' }}
        </button>
      </div>

      <div v-if="error" class="error-message">
        ❌ {{ error }}
      </div>

      <div v-if="result" class="result-section">
        <h3 class="result-title">分析结果</h3>
        
        <div class="result-card">
          <div class="result-item">
            <span class="label">类型：</span>
            <span class="value type-badge" :class="result.type">
              {{ result.type === 'video' ? '🎥 视频' : '🖼️ 图文' }}
            </span>
          </div>
          
          <div class="result-item">
            <span class="label">标题：</span>
            <span class="value">{{ result.title }}</span>
          </div>
          
          <div v-if="result.description" class="result-item">
            <span class="label">描述：</span>
            <span class="value">{{ result.description }}</span>
          </div>
          
          <div v-if="result.video_id" class="result-item">
            <span class="label">视频ID：</span>
            <span class="value">{{ result.video_id }}</span>
          </div>
          
          <div v-if="result.video_url" class="result-item">
            <span class="label">视频链接：</span>
            <a :href="result.video_url" target="_blank" class="value link">{{ result.video_url }}</a>
          </div>
          
          <div v-if="result.image_url" class="result-item">
            <span class="label">图片链接：</span>
            <a :href="result.image_url" target="_blank" class="value link">{{ result.image_url }}</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DouyinAnalyzer',
  data() {
    return {
      douyinUrl: '',
      loading: false,
      error: null,
      result: null
    }
  },
  methods: {
    async analyzeUrl() {
      if (!this.douyinUrl.trim()) {
        this.error = '请输入抖音链接'
        return
      }

      this.loading = true
      this.error = null
      this.result = null

      try {
        const response = await axios.post('http://localhost:8000/api/analyze-douyin/', {
          url: this.douyinUrl
        })

        if (response.data.success) {
          this.result = response.data.data
        } else {
          this.error = response.data.error || '分析失败'
        }
      } catch (err) {
        this.error = err.response?.data?.error || '网络错误，请检查后端服务是否运行'
        console.error('Error:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.douyin-analyzer {
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

.input-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.url-input {
  flex: 1;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.url-input:focus {
  outline: none;
  border-color: #667eea;
}

.analyze-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.analyze-btn:disabled {
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

.result-section {
  margin-top: 2rem;
}

.result-title {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.result-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
}

.result-item {
  display: flex;
  margin-bottom: 1rem;
  align-items: flex-start;
}

.result-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
}

.value {
  color: #333;
  flex: 1;
}

.type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-weight: 600;
}

.type-badge.video {
  background: #e3f2fd;
  color: #1976d2;
}

.type-badge.image {
  background: #f3e5f5;
  color: #7b1fa2;
}

.link {
  color: #667eea;
  text-decoration: none;
  word-break: break-all;
}

.link:hover {
  text-decoration: underline;
}
</style>

