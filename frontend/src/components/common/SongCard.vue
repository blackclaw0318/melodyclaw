<template>
  <div 
    class="song-card bg-white rounded-2xl shadow-lg overflow-hidden cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-xl"
    @click="handleClick"
    data-testid="song-card"
  >
    <!-- 封面图 -->
    <div class="song-cover relative aspect-square bg-gradient-to-br from-primary to-secondary overflow-hidden">
      <img 
        v-if="song.cover_url" 
        :src="song.cover_url" 
        :alt="song.title"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-white text-6xl">
        🎵
      </div>
      
      <!-- 时长标签 -->
      <div class="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
        {{ formattedDuration }}
      </div>
      
      <!-- 播放按钮（hover 显示） -->
      <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
        <div class="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center">
          <svg class="w-8 h-8 text-primary ml-1" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </div>
      </div>
    </div>
    
    <!-- 歌曲信息 -->
    <div class="p-4">
      <h3 class="font-bold text-lg text-gray-800 truncate" :title="song.title">
        {{ song.title }}
      </h3>
      <p class="text-sm text-gray-500 mt-1 truncate" :title="song.artist || '未知歌手'">
        {{ song.artist || '未知歌手' }}
      </p>
      
      <!-- 统计信息 -->
      <div class="flex items-center justify-between mt-3 text-xs text-gray-400">
        <div class="flex items-center gap-1">
          <span>🎤</span>
          <span>{{ song.duet_count || 0 }} 次合唱</span>
        </div>
        <div class="flex items-center gap-1">
          <span>🎵</span>
          <span>{{ song.bpm || '--' }} BPM</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  song: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const formattedDuration = computed(() => {
  if (!props.song.duration) return '--:--'
  const mins = Math.floor(props.song.duration / 60)
  const secs = Math.floor(props.song.duration % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
})

function handleClick() {
  router.push(`/record/${props.song.id}`)
}
</script>

<style scoped>
.song-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
