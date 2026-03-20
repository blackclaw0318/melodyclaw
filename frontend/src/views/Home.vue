<template>
  <div class="home min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
    <!-- 顶部导航栏 -->
    <header class="sticky top-0 z-40 bg-white/80 backdrop-blur-lg shadow-sm">
      <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 class="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          🦞 MelodyClaw
        </h1>
        <div class="flex items-center gap-3">
          <button class="p-2 text-gray-600 hover:text-primary">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </button>
          <button class="p-2 text-gray-600 hover:text-primary">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- 主要内容区 -->
    <main class="max-w-6xl mx-auto px-4 py-6">
      <!-- 欢迎横幅 -->
      <div class="mb-6 bg-gradient-to-r from-primary to-secondary rounded-2xl p-6 text-white shadow-lg">
        <h2 class="text-2xl font-bold mb-2">想唱就唱 🎤</h2>
        <p class="opacity-90">选择一首歌曲，开始你的表演！</p>
      </div>

      <!-- 搜索和筛选 -->
      <div class="mb-6 space-y-3">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索歌曲或歌手..."
            class="w-full px-4 py-3 pl-12 bg-white rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
          />
          <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        
        <div class="flex gap-2 overflow-x-auto pb-2">
          <button
            v-for="cat in categories"
            :key="cat.id"
            @click="selectedCategory = cat.id"
            class="px-4 py-2 rounded-full whitespace-nowrap transition-all"
            :class="selectedCategory === cat.id ? 'bg-primary text-white' : 'bg-white text-gray-600 hover:bg-gray-100'"
          >
            {{ cat.name }}
          </button>
        </div>
      </div>

      <!-- 歌曲列表 -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>

      <div v-else-if="filteredSongs.length === 0" class="text-center py-20">
        <div class="text-6xl mb-4">🎵</div>
        <p class="text-gray-500">暂无歌曲</p>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4" data-testid="song-list">
        <SongCard
          v-for="song in filteredSongs"
          :key="song.id"
          :song="song"
        />
      </div>
    </main>

    <!-- 底部小龙虾动画 -->
    <div class="fixed bottom-4 right-4 z-30">
      <LobsterAnimation :is-playing="true" :initial-position="{ x: 0, y: 0 }" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SongCard from '@/components/common/SongCard.vue'
import LobsterAnimation from '@/components/lobster/LobsterAnimation.vue'
import { songsApi } from '@/api/songs'

const searchQuery = ref('')
const selectedCategory = ref('all')
const songs = ref([])
const loading = ref(true)

const categories = [
  { id: 'all', name: '全部' },
  { id: 'pop', name: '流行' },
  { id: 'rock', name: '摇滚' },
  { id: 'folk', name: '民谣' },
  { id: 'ballad', name: '抒情' }
]

const filteredSongs = computed(() => {
  let result = songs.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(song => 
      song.title.toLowerCase().includes(query) ||
      (song.artist && song.artist.toLowerCase().includes(query))
    )
  }
  
  // 分类过滤（暂时按 BPM 简单分类）
  if (selectedCategory.value !== 'all') {
    // 后续可以根据实际分类字段过滤
  }
  
  return result
})

onMounted(async () => {
  try {
    const data = await songsApi.getList()
    songs.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('获取歌曲列表失败:', error)
    // 使用测试数据
    songs.value = [
      {
        id: 1,
        title: '测试歌曲 - 青花瓷',
        artist: '周杰伦',
        duration: 239,
        bpm: 120,
        duet_count: 128,
        cover_url: null
      },
      {
        id: 2,
        title: '测试歌曲 - 告白气球',
        artist: '周杰伦',
        duration: 215,
        bpm: 100,
        duet_count: 256,
        cover_url: null
      }
    ]
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home {
  padding-bottom: 100px;
}

/* 隐藏滚动条但保持滚动功能 */
.overflow-x-auto::-webkit-scrollbar {
  height: 4px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 2px;
}
</style>
