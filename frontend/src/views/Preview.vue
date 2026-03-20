<template>
  <div class="preview-page min-h-screen bg-gray-900 text-white">
    <!-- 顶部导航 -->
    <header class="sticky top-0 z-40 bg-gray-900/80 backdrop-blur-lg border-b border-gray-800">
      <div class="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <button 
          @click="goBack"
          class="p-2 text-gray-400 hover:text-white transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        
        <h1 class="text-lg font-semibold">预览</h1>
        
        <div class="w-10"></div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="max-w-4xl mx-auto px-4 py-6">
      <!-- 视频播放器 -->
      <div class="relative aspect-[9/16] max-h-[70vh] bg-black rounded-2xl overflow-hidden shadow-2xl mx-auto">
        <video
          v-if="videoUrl"
          ref="videoRef"
          :src="videoUrl"
          class="w-full h-full object-cover"
          controls
          playsinline
        />
        
        <div v-else class="absolute inset-0 flex items-center justify-center">
          <div class="text-center">
            <div class="text-6xl mb-4">🎬</div>
            <p class="text-gray-400">视频加载中...</p>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="mt-6 flex flex-col gap-3">
        <!-- 主要操作 -->
        <div class="grid grid-cols-2 gap-3">
          <button
            @click="reRecord"
            class="py-4 px-6 bg-gray-800 hover:bg-gray-700 rounded-xl font-medium transition-all flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            重录
          </button>
          
          <button
            @click="downloadVideo"
            class="py-4 px-6 bg-primary hover:bg-primary/90 rounded-xl font-medium transition-all flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            保存
          </button>
        </div>
        
        <!-- 分享按钮（P2 功能） -->
        <button
          @click="shareVideo"
          class="py-4 px-6 bg-gray-800 hover:bg-gray-700 rounded-xl font-medium transition-all flex items-center justify-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
          </svg>
          分享
        </button>
      </div>

      <!-- 歌曲信息 -->
      <div v-if="recording && song" class="mt-6 p-4 bg-gray-800 rounded-xl">
        <h3 class="font-semibold text-lg">{{ song.title }}</h3>
        <p class="text-gray-400 text-sm mt-1">{{ song.artist }}</p>
        
        <div class="flex items-center gap-4 mt-3 text-sm text-gray-400">
          <span>时长：{{ formattedDuration }}</span>
          <span>•</span>
          <span>{{ new Date(recording.created_at).toLocaleString('zh-CN') }}</span>
        </div>
      </div>
    </main>

    <!-- 下载提示 -->
    <div v-if="showDownloadToast" class="fixed bottom-20 left-1/2 -translate-x-1/2 bg-green-600 text-white px-6 py-3 rounded-full shadow-lg animate-fade-in">
      ✓ 下载已开始
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { recordingsApi } from '@/api/recordings'
import { songsApi } from '@/api/songs'

const route = useRoute()
const router = useRouter()
const recordingId = route.params.id

const videoRef = ref(null)
const videoUrl = ref(null)
const recording = ref(null)
const song = ref(null)
const showDownloadToast = ref(false)

const formattedDuration = computed(() => {
  if (!recording.value?.duration) return '--:--'
  const mins = Math.floor(recording.value.duration / 60)
  const secs = Math.floor(recording.value.duration % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
})

onMounted(async () => {
  if (recordingId === 'local') {
    // 本地预览（上传失败的情况）
    return
  }
  
  try {
    // 加载作品信息
    recording.value = await recordingsApi.getById(recordingId)
    
    // 加载歌曲信息
    if (recording.value?.song_id) {
      song.value = await songsApi.getById(recording.value.song_id)
    }
    
    // 加载视频
    videoUrl.value = await recordingsApi.getVideo(recordingId)
  } catch (error) {
    console.error('加载预览失败:', error)
  }
})

function goBack() {
  router.push('/')
}

function reRecord() {
  if (song.value) {
    router.push(`/record/${song.value.id}`)
  } else {
    router.push('/')
  }
}

async function downloadVideo() {
  try {
    if (!videoUrl.value) return
    
    const link = document.createElement('a')
    link.href = videoUrl.value
    link.download = `melodyclaw_recording_${recordingId}.webm`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    showDownloadToast.value = true
    setTimeout(() => {
      showDownloadToast.value = false
    }, 2000)
  } catch (error) {
    console.error('下载失败:', error)
    alert('下载失败，请重试')
  }
}

function shareVideo() {
  // P2 功能：分享
  if (navigator.share) {
    navigator.share({
      title: '我的 MelodyClaw 作品',
      text: `我在 MelodyClaw 合唱了 ${song.value?.title || '一首歌'}！`,
      url: window.location.href
    }).catch(console.error)
  } else {
    // 复制链接
    navigator.clipboard.writeText(window.location.href)
    alert('链接已复制到剪贴板')
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, 20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>
