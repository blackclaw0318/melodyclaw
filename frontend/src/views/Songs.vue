<template>
  <div class="songs">
    <h1>🎵 歌曲管理</h1>
    <p class="hint">上传歌曲后，依次进行：人声分离 → 歌词对齐 → 音色克隆</p>
    
    <!-- 上传区域 -->
    <div class="upload-card">
      <input type="file" ref="fileInput" @change="onFile" accept=".mp3,.wav,.flac,.m4a,.ogg" hidden />
      <button @click="$refs.fileInput.click()" class="btn">📁 选择文件</button>
      <span v-if="selectedFile" class="file-info">{{ selectedFile.name }} ({{ (selectedFile.size/1024/1024).toFixed(2) }} MB)</span>
      <button v-if="selectedFile" @click="upload" :disabled="uploading" class="btn-upload">
        {{ uploading ? '上传中...' : '上传' }}
      </button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="songs.length === 0" class="empty">暂无歌曲，上传第一首吧！</div>
    
    <div v-else class="list">
      <div v-for="s in songs" :key="s.id" class="song-card">
        <div class="song-header">
          <div class="song-icon">🎵</div>
          <div class="song-info">
            <h3>{{ s.title }}</h3>
            <div class="meta">
              <span v-if="s.artist">👤 {{ s.artist }}</span>
              <span>⏱️ {{ s.duration ? s.duration.toFixed(1) + 's' : '-' }}</span>
              <span class="status-badge" :class="s.status">{{ statusText(s.status) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 操作流程 -->
        <div class="workflow">
          <!-- 步骤 1: 人声分离 -->
          <div class="step" :class="getStepClass(s, 'vocals')">
            <div class="step-num">1</div>
            <div class="step-info">
              <div class="step-title">人声分离</div>
              <div class="step-desc">分离人声和伴奏</div>
            </div>
            <button @click="separateVocals(s)" 
                    :disabled="s.status !== 'uploaded' && s.status !== 'separated'"
                    class="step-btn">
              {{ s.has_vocals ? '✓' : '分离' }}
            </button>
          </div>
          
          <!-- 步骤 2: 歌词对齐 -->
          <div class="step" :class="getStepClass(s, 'lyrics')">
            <div class="step-num">2</div>
            <div class="step-info">
              <div class="step-title">歌词对齐</div>
              <div class="step-desc">生成时间戳</div>
            </div>
            <button @click="showLyricsDialog(s)" 
                    :disabled="!s.has_vocals"
                    class="step-btn">
              {{ s.has_aligned_lyrics ? '✓' : '对齐' }}
            </button>
          </div>
          
          <!-- 步骤 3: 音色克隆 -->
          <div class="step" :class="getStepClass(s, 'clone')">
            <div class="step-num">3</div>
            <div class="step-info">
              <div class="step-title">音色克隆</div>
              <div class="step-desc">6 种音色可选</div>
            </div>
            <button @click="showCloneDialog(s)" 
                    :disabled="!s.has_vocals"
                    class="step-btn">
              {{ s.has_cloned ? '✓' : '克隆' }}
            </button>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="actions">
          <button @click="playSong(s)" class="btn-icon" title="播放">▶️</button>
          <button @click="del(s.id)" class="btn-icon delete" title="删除">🗑️</button>
        </div>
      </div>
    </div>
    
    <!-- 歌词对话框 -->
    <div v-if="showLyrics" class="dialog-overlay" @click.self="showLyrics = false">
      <div class="dialog">
        <h3>📝 歌词对齐 - {{ currentSong?.title }}</h3>
        <textarea v-model="lyricsText" placeholder="输入歌词，每行一句..." rows="10"></textarea>
        <div class="dialog-actions">
          <button @click="showLyrics = false" class="btn-cancel">取消</button>
          <button @click="alignLyrics" :disabled="aligning" class="btn-ok">
            {{ aligning ? '对齐中...' : '开始对齐' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 克隆对话框 -->
    <div v-if="showClone" class="dialog-overlay" @click.self="showClone = false">
      <div class="dialog">
        <h3>🎤 音色克隆 - {{ currentSong?.title }}</h3>
        <div class="voice-select">
          <div v-for="v in voices" :key="v.id" 
               class="voice-option" :class="{ selected: selectedVoice === v.id }"
               @click="selectedVoice = v.id">
            <div class="voice-icon">🎤</div>
            <div class="voice-name">{{ v.name }}</div>
            <div class="voice-style">{{ v.style }}</div>
          </div>
        </div>
        <div class="dialog-actions">
          <button @click="showClone = false" class="btn-cancel">取消</button>
          <button @click="cloneVoice" :disabled="cloning || !selectedVoice" class="btn-ok">
            {{ cloning ? '克隆中...' : '开始克隆' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_BASE = 'http://111.228.46.221:8000/api/v1'

const songs = ref([])
const loading = ref(false)
const selectedFile = ref(null)
const uploading = ref(false)
const showLyrics = ref(false)
const showClone = ref(false)
const currentSong = ref(null)
const lyricsText = ref('')
const aligning = ref(false)
const cloning = ref(false)
const selectedVoice = ref('pop_male')
const voices = ref([])

const statusText = (s) => {
  const map = { uploaded: '已上传', separated: '已分离', aligned: '已对齐', cloned: '已克隆' }
  return map[s] || s
}

const getStepClass = (s, step) => {
  if (step === 'vocals') return s.has_vocals ? 'done' : ''
  if (step === 'lyrics') return s.has_aligned_lyrics ? 'done' : (!s.has_vocals ? 'locked' : '')
  if (step === 'clone') return s.has_cloned ? 'done' : (!s.has_vocals ? 'locked' : '')
  return ''
}

onMounted(async () => {
  await fetchSongs()
  await fetchVoices()
})

const fetchSongs = async () => {
  loading.value = true
  try {
    const r = await axios.get(`${API_BASE}/songs`)
    songs.value = r.data
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

const fetchVoices = async () => {
  try {
    const r = await axios.get(`${API_BASE}/voices`)
    voices.value = r.data
  } catch (e) {
    console.error(e)
  }
}

const onFile = (e) => { selectedFile.value = e.target.files[0] }

const upload = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('title', selectedFile.value.name.replace(/\.[^.]+$/, ''))
    await axios.post(`${API_BASE}/songs`, formData)
    selectedFile.value = null
    alert('上传成功!')
    await fetchSongs()
  } catch (e) {
    alert('上传失败：' + e.message)
  }
  uploading.value = false
}

const separateVocals = async (song) => {
  if (!confirm(`确定对"${song.title}"进行人声分离？`)) return
  try {
    const r = await axios.post(`${API_BASE}/songs/${song.id}/separate`)
    alert('人声分离完成!')
    await fetchSongs()
  } catch (e) {
    alert('分离失败：' + e.message)
  }
}

const showLyricsDialog = (song) => {
  currentSong.value = song
  lyricsText.value = ''
  showLyrics.value = true
}

const alignLyrics = async () => {
  if (!lyricsText.value) return
  aligning.value = true
  try {
    await axios.post(`${API_BASE}/lyrics/${currentSong.value.id}/align`, {
      song_id: currentSong.value.id,
      lyrics: lyricsText.value
    })
    showLyrics.value = false
    alert('歌词对齐完成!')
    await fetchSongs()
  } catch (e) {
    alert('对齐失败：' + e.message)
  }
  aligning.value = false
}

const showCloneDialog = (song) => {
  currentSong.value = song
  selectedVoice.value = 'pop_male'
  showClone.value = true
}

const cloneVoice = async () => {
  cloning.value = true
  try {
    const r = await axios.post(`${API_BASE}/clone`, {
      song_id: currentSong.value.id,
      voice_id: selectedVoice.value
    })
    showClone.value = false
    alert('克隆完成!')
    await fetchSongs()
  } catch (e) {
    alert('克隆失败：' + e.message)
  }
  cloning.value = false
}

const playSong = (song) => {
  alert('播放功能开发中...')
}

const del = async (id) => {
  if (!confirm('确定删除？')) return
  await axios.delete(`${API_BASE}/songs/${id}`)
  await fetchSongs()
}
</script>

<style scoped>
.songs { max-width: 1000px; margin: 0 auto; }
h1 { margin-bottom: 0.5rem; }
.hint { color: #999; margin-bottom: 2rem; }
.upload-card { background: white; padding: 1.5rem; border-radius: 1rem; margin-bottom: 2rem; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.btn, .btn-upload { padding: 0.75rem 1.5rem; background: #667eea; color: white; border: none; border-radius: 0.5rem; cursor: pointer; }
.btn-upload { background: #388e3c; }
.btn-upload:disabled { opacity: 0.5; }
.file-info { color: #666; font-size: 0.9rem; }
.list { display: flex; flex-direction: column; gap: 1.5rem; }
.song-card { background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
.song-header { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.song-icon { font-size: 3rem; }
.song-info h3 { margin-bottom: 0.5rem; }
.meta { display: flex; gap: 1rem; color: #999; font-size: 0.85rem; align-items: center; }
.status-badge { padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; }
.status-badge.uploaded { background: #e3f2fd; color: #1976d2; }
.status-badge.separated { background: #e8f5e9; color: #388e3c; }
.status-badge.aligned { background: #fff3e0; color: #f57c00; }
.status-badge.cloned { background: #f3e5f5; color: #7b1fa2; }
.workflow { display: flex; gap: 1rem; margin-bottom: 1rem; }
.step { flex: 1; display: flex; align-items: center; gap: 0.75rem; padding: 1rem; background: #f8f9fa; border-radius: 0.5rem; border: 2px solid #eee; }
.step.done { border-color: #388e3c; background: #e8f5e9; }
.step.locked { opacity: 0.5; }
.step-num { width: 30px; height: 30px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.step.done .step-num { background: #388e3c; }
.step-info { flex: 1; }
.step-title { font-weight: 500; margin-bottom: 0.25rem; }
.step-desc { color: #999; font-size: 0.8rem; }
.step-btn { padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 0.5rem; cursor: pointer; }
.step-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-icon { padding: 0.5rem; background: none; border: none; cursor: pointer; font-size: 1.2rem; border-radius: 0.5rem; }
.btn-icon:hover { background: #f0f0f0; }
.btn-icon.delete:hover { background: #ffebee; }
.loading, .empty { text-align: center; padding: 3rem; background: white; border-radius: 1rem; color: #999; }
.dialog-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: white; padding: 2rem; border-radius: 1rem; width: 90%; max-width: 500px; max-height: 80vh; overflow-y: auto; }
.dialog h3 { margin-bottom: 1rem; }
textarea { width: 100%; padding: 1rem; border: 1px solid #ddd; border-radius: 0.5rem; font-family: inherit; resize: vertical; margin-bottom: 1rem; }
.voice-select { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-bottom: 1rem; }
.voice-option { border: 2px solid #eee; border-radius: 0.5rem; padding: 1rem; text-align: center; cursor: pointer; }
.voice-option:hover { border-color: #667eea; }
.voice-option.selected { border-color: #667eea; background: #f0f4ff; }
.voice-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.voice-name { font-weight: 500; margin-bottom: 0.25rem; }
.voice-style { color: #999; font-size: 0.8rem; }
.dialog-actions { display: flex; gap: 1rem; justify-content: flex-end; }
.btn-cancel { padding: 0.75rem 1.5rem; background: #f0f0f0; border: none; border-radius: 0.5rem; cursor: pointer; }
.btn-ok { padding: 0.75rem 1.5rem; background: #667eea; color: white; border: none; border-radius: 0.5rem; cursor: pointer; }
.btn-ok:disabled { opacity: 0.5; }
</style>
