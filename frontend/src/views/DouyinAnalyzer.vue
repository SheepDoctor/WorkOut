<template>
  <div class="w-full max-w-lg h-full flex flex-col p-6 relative overflow-hidden">
    <div class="glass-card p-8 rounded-[2.5rem] shadow-2xl overflow-y-auto flex-1">
      <header class="mb-8">
        <router-link to="/" class="text-blue-400 text-sm font-semibold tracking-widest uppercase mb-4 block hover:underline">
          <i class="fa-solid fa-arrow-left mr-2"></i> 返回主页
        </router-link>
        <h1 class="text-4xl font-bold text-white mb-2 leading-tight">抖音分析</h1>
        <p class="text-slate-400 text-sm">输入链接，获取详细信息</p>
      </header>
      
      <div class="space-y-4 mb-8">
        <input
          v-model="douyinUrl"
          type="text"
          placeholder="请输入抖音链接..."
          class="w-full bg-slate-900/40 border border-white/10 rounded-2xl p-4 text-white focus:outline-none focus:border-blue-500 transition-colors"
        />
        <button @click="analyzeUrl" :disabled="loading" 
                class="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-2xl font-bold text-white transition-all shadow-lg shadow-blue-500/20">
          {{ loading ? '分析中...' : '分析链接' }}
        </button>
      </div>

      <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-2xl mb-6 text-sm">
        {{ error }}
      </div>

      <div v-if="result" class="space-y-6">
        <h3 class="text-xs font-bold text-slate-500 tracking-widest uppercase">分析结果</h3>
        
        <div class="bg-slate-900/40 rounded-3xl p-6 border border-white/5 space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-xs text-slate-500 uppercase font-bold">类型</span>
            <span :class="['px-3 py-1 rounded-full text-[10px] font-bold uppercase', 
                           result.type === 'video' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400']">
              {{ result.type === 'video' ? '视频' : '图文' }}
            </span>
          </div>
          
          <div class="space-y-1">
            <span class="text-xs text-slate-500 uppercase font-bold">标题</span>
            <p class="text-sm text-white leading-relaxed">{{ result.title }}</p>
          </div>
          
          <div v-if="result.description" class="space-y-1">
            <span class="text-xs text-slate-500 uppercase font-bold">描述</span>
            <p class="text-sm text-slate-400 leading-relaxed">{{ result.description }}</p>
          </div>

          <div v-if="result.video_url || result.image_url" class="pt-4 border-t border-white/5">
            <a :href="result.video_url || result.image_url" target="_blank" 
               class="text-blue-400 text-xs font-bold hover:text-blue-300 transition-colors flex items-center gap-2">
              查看原始资源 <i class="fa-solid fa-external-link text-[10px]"></i>
            </a>
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
.glass-card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>

