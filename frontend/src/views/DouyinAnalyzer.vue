<template>
  <div class="w-full max-w-lg h-full flex flex-col p-6 relative overflow-hidden">
    <div class="glass-card p-8 rounded-[2.5rem] shadow-2xl overflow-y-auto flex-1">
      <header class="mb-8">
        <router-link to="/" class="text-cyan-300 text-sm font-semibold tracking-widest uppercase mb-4 block hover:underline hover:text-cyan-200 transition-colors">
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
          class="w-full bg-gradient-to-br from-indigo-900/40 to-slate-900/40 border border-cyan-500/20 rounded-2xl p-4 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:shadow-lg focus:shadow-cyan-500/20 transition-all"
        />
        <button @click="analyzeUrl" :disabled="loading" 
                class="w-full py-4 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed rounded-2xl font-bold text-white transition-all shadow-lg shadow-cyan-500/50 hover:shadow-cyan-400/60 hover:scale-105">
          {{ loading ? '分析中...' : '分析链接' }}
        </button>
      </div>

      <div v-if="error" class="bg-gradient-to-br from-red-500/15 to-pink-500/10 border border-red-400/30 text-red-300 p-4 rounded-2xl mb-6 text-sm shadow-lg shadow-red-500/20">
        {{ error }}
      </div>

      <div v-if="result" class="space-y-6">
        <h3 class="text-xs font-bold text-cyan-400 tracking-widest uppercase">分析结果</h3>
        
        <div class="bg-gradient-to-br from-indigo-900/40 to-purple-900/30 rounded-3xl p-6 border border-cyan-500/20 space-y-4 shadow-lg">
          <div class="flex justify-between items-center">
            <span class="text-xs text-slate-400 uppercase font-bold">类型</span>
            <span :class="['px-3 py-1 rounded-full text-[10px] font-bold uppercase shadow-lg', 
                           result.type === 'video' ? 'bg-gradient-to-r from-cyan-500/30 to-blue-500/30 text-cyan-300 border border-cyan-400/30' : 'bg-gradient-to-r from-purple-500/30 to-fuchsia-500/30 text-purple-300 border border-purple-400/30']">
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

          <div v-if="result.video_url || result.image_url" class="pt-4 border-t border-cyan-500/20">
            <a :href="result.video_url || result.image_url" target="_blank" 
               class="text-cyan-300 text-xs font-bold hover:text-cyan-200 transition-all hover:drop-shadow-[0_0_8px_rgba(34,211,238,0.5)] flex items-center gap-2">
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
        const response = await axios.post('/api/analyze-douyin/', {
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
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(147, 197, 253, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}
</style>

