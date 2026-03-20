<template>
  <div class="record-page fixed inset-0 bg-black overflow-hidden">
    <!-- 顶部控制栏 -->
    <header class="absolute top-0 left-0 right-0 z-40 p-4 flex items-center justify-between">
      <button 
        @click="goBack"
        class="p-2 bg-black/40 backdrop-blur-md rounded-full text-white hover:bg-black/60 transition-all"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      
      <div class="text-white font-medium">
        {{ song?.title || '拍摄中' }}
      </div>
      
      <button 
        @click="switchCamera"
        class="p-2 bg-black/40 backdrop-blur-md rounded-full text-white hover:bg-black/60 transition-all"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
      </button>
    </header>

    <!-- 摄像头视图 -->
    <CameraView
      ref="cameraRef"
      @stream-ready="onStreamReady"
      @error="onCameraError"
    >
      <template #interactive>
        <!-- 小龙虾动画 -->
        <LobsterAnimation
          v-if="showLobster"
          ref="lobsterRef"
          :is-playing="isPlaying"
          :locked="isRecording"
          :initial-position="lobsterPosition"
          @position-change="onLobsterPositionChange"
        />
        
        <!-- 歌词字幕 -->
        <LyricsScroll
          v-if="showLyrics && lyrics.length > 0"
          ref="lyricsRef"
          :lyrics="lyrics"
          :current-index="currentLyricIndex"
          :locked="isRecording"
          :initial-position="lyricsPosition"
          @position-change="onLyricsPositionChange"
        />
      </template>
      
      <template #controls>
        <!-- 底部控制区 -->
        <div class="flex flex-col items-center gap-4 pb-4">
          <!-- 功能切换按钮 -->
          <div class="flex gap-4">
            <button
              @click="toggleLobster"
              class="px-4 py-2 rounded-full text-sm font-medium transition-all"
              :class="showLobster ? 'bg-lobster text-white' : 'bg-white/20 text-white backdrop-blur-md'"
            >
              🦞 动画
            </button>
            <button
              @click="toggleLyrics"
              class="px-4 py-2 rounded-full text-sm font-medium transition-all"
              :class="showLyrics ? 'bg-primary text-white' : 'bg-white/20 text-white backdrop-blur-md'"
            >
              📝 歌词
            </button>
          </div>
          
          <!-- 录制按钮 -->
          <Recorder
            ref="recorderRef"
            :countdown-duration="countdownDuration"
            :bpm="song?.bpm || 120"
            @start="onRecordingStart"
            @stop="onRecordingStop"
          />
        </div>
      </template>
    </CameraView>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="absolute inset-0 z-50 flex items-center justify-center bg-black/80">
      <div class="text-center text-white p-4">
        <p class="text-xl mb-2">⚠️ {{ errorMessage }}</p>
        <button 
          @click="goBack" 
          class="mt-4 px-6 py-2 bg-primary rounded-lg hover:bg-primary/80"
        >
          返回
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CameraView from '@/components/camera/CameraView.vue'
import LobsterAnimation from '@/components/lobster/LobsterAnimation.vue'
import LyricsScroll from '@/components/lyrics/LyricsScroll.vue'
import Recorder from '@/components/recorder/Recorder.vue'
import { songsApi } from '@/api/songs'
import { recordingsApi } from '@/api/recordings'
import { useRecorder } from '@/composables/useRecorder'

const route = useRoute()
const router = useRouter()
const songId = route.params.songId

const cameraRef = ref(null)
const lobsterRef = ref(null)
const lyricsRef = ref(null)
const recorderRef = ref(null)

const song = ref(null)
const lyrics = ref([])
const currentLyricIndex = ref(-1)
const isPlaying = ref(false)
const isRecording = ref(false)
const errorMessage = ref('')

const showLobster = ref(true)
const showLyrics = ref(true)
const countdownDuration = ref(3)

const lobsterPosition = ref({ x: 50, y: 100 })
const lyricsPosition = ref({ x: 50, y: 300 })

let audioElement = null
let lyricsTimer = null

// 加载歌曲信息
onMounted(async () => {
  try {
    song.value = await songsApi.getById(songId)
    await loadLyrics()
  } catch (error) {
    console.error('加载歌曲失败:', error)
    errorMessage.value = '加载歌曲失败，请重试'
  }
})

onUnmounted(() => {
  if (audioElement) {
    audioElement.pause()
    audioElement = null
  }
  if (lyricsTimer) {
    clearInterval(lyricsTimer)
  }
})

async function loadLyrics() {
  try {
    // 获取歌词（如果有对齐后的歌词）
    if (song.value?.has_aligned_lyrics) {
      const data = await songsApi.getLyrics(songId)
      lyrics.value = Array.isArray(data) ? data : JSON.parse(data || '[]')
    } else {
      // 使用测试歌词
      lyrics.value = [
        { time: 0, text: '素胚勾勒出青花笔锋浓转淡' },
        { time: 5, text: '瓶身描绘的牡丹一如你初妆' },
        { time: 10, text: '冉冉檀香透过窗心事我了然' },
        { time: 15, text: '宣纸上走笔至此搁一半' }
      ]
    }
  } catch (error) {
    console.error('加载歌词失败:', error)
  }
}

function onStreamReady(stream) {
  console.log('摄像头流已就绪')
}

function onCameraError(error) {
  console.error('摄像头错误:', error)
  errorMessage.value = '无法访问摄像头，请检查权限设置'
}

function switchCamera() {
  cameraRef.value?.switchCamera()
}

function toggleLobster() {
  showLobster.value = !showLobster.value
}

function toggleLyrics() {
  showLyrics.value = !showLyrics.value
}

function onLobsterPositionChange(pos) {
  lobsterPosition.value = pos
}

function onLyricsPositionChange(pos) {
  lyricsPosition.value = pos
}

async function onRecordingStart() {
  isRecording.value = true
  isPlaying.value = true
  
  // 获取伴奏 URL
  const accompanimentUrl = await songsApi.getAccompaniment(songId).catch(() => null)
  
  // 开始录制
  const cameraStream = cameraRef.value?.getStream()
  if (cameraStream) {
    await useRecorder().startRecording({
      cameraStream,
      accompanimentUrl
    })
  }
  
  // 开始歌词同步
  startLyricsSync()
}

function onRecordingStop(duration) {
  isRecording.value = false
  isPlaying.value = false
  
  // 停止歌词同步
  if (lyricsTimer) {
    clearInterval(lyricsTimer)
    lyricsTimer = null
  }
  
  // 停止音频
  if (audioElement) {
    audioElement.pause()
    audioElement = null
  }
  
  // 上传作品
  uploadRecording(duration)
}

function startLyricsSync() {
  const startTime = Date.now()
  
  lyricsTimer = setInterval(() => {
    const elapsed = (Date.now() - startTime) / 1000
    
    // 找到当前应该显示的歌词
    for (let i = lyrics.value.length - 1; i >= 0; i--) {
      if (elapsed >= lyrics.value[i].time) {
        currentLyricIndex.value = i
        break
      }
    }
  }, 100)
}

async function uploadRecording(duration) {
  try {
    // 获取录制的视频 blob
    const recordedBlob = useRecorder().getRecordedBlob()
    
    // 创建 FormData
    const formData = new FormData()
    formData.append('song_id', songId)
    formData.append('video', recordedBlob, 'recording.webm')
    formData.append('lobster_position', JSON.stringify(lobsterRef.value?.getPosition() || lobsterPosition.value))
    formData.append('lyrics_position', JSON.stringify(lyricsRef.value?.getPosition() || lyricsPosition.value))
    
    // 上传
    const result = await recordingsApi.upload(formData)
    
    // 跳转到预览页面
    router.push(`/preview/${result.id}`)
  } catch (error) {
    console.error('上传失败:', error)
    // 上传失败也跳转到预览（本地预览）
    router.push(`/preview/local`)
  }
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.record-page {
  touch-action: none;
}
</style>
