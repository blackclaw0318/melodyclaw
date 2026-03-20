<template>
  <div class="clone">
    <h1>🎤 音色克隆</h1>
    <p class="hint">选择一首已分离人声的歌曲，使用不同音色重新演唱</p>

    <div class="card">
      <label>选择歌曲：</label>
      <select v-model="selectedSongId">
        <option value="">请选择...</option>
        <option v-for="song in songs" :key="song.id" :value="song.id" :disabled="!song.has_vocals">
          {{ song.title }} {{ song.has_vocals ? '✓' : '(需先分离)' }}
        </option>
      </select>
    </div>

    <div v-if="selectedSongId" class="card">
      <label>选择音色：</label>
      <div class="voice-grid">
        <div v-for="voice in voices" :key="voice.id" 
             class="voice-card" :class="{ selected: selectedVoice === voice.id }"
             @click="selectedVoice = voice.id">
          <div class="voice-icon">🎤</div>
          <div class="voice-name">{{ voice.name }}</div>
          <div class="voice-style">{{ voice.style }}</div>
        </div>
      </div>
    </div>

    <div v-if="selectedSongId && selectedVoice" class="card">
      <button @click="startClone" :disabled="cloning" class="btn-clone">
        {{ cloning ? '克隆中...' : '🚀 开始克隆' }}
      </button>
    </div>

    <div v-if="result" class="card result">
      <h3>克隆结果</h3>
      <p>状态：{{ result.status }}</p>
      <p v-if="result.processing_time">耗时：{{ result.processing_time.toFixed(2) }}s</p>
      <a v-if="result.output_path" :href="result.output_path" class="btn-download">⬇️ 下载</a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSongStore, useCloneStore } from '../stores'

const songStore = useSongStore()
const cloneStore = useCloneStore()

const selectedSongId = ref('')
const selectedVoice = ref('')
const cloning = ref(false)
const result = ref(null)

const songs = computed(() => songStore.songs)
const voices = computed(() => cloneStore.voices)

onMounted(async () => {
  await songStore.fetchSongs()
  await cloneStore.fetchVoices()
  if (voices.value.length > 0) {
    selectedVoice.value = voices.value[0].id
  }
})

const startClone = async () => {
  if (!selectedSongId.value || !selectedVoice.value) return
  cloning.value = true
  try {
    const axios = (await import('axios')).default
    const r = await axios.post('/api/v1/clone', {
      song_id: selectedSongId.value,
      voice_id: selectedVoice.value
    })
    result.value = r.data
  } catch (e) {
    alert('克隆失败：' + e.message)
  }
  cloning.value = false
}
</script>

<style scoped>
.clone { max-width: 800px; margin: 0 auto; }
h1 { margin-bottom: 0.5rem; }
.hint { color: #999; margin-bottom: 2rem; }
.card { background: white; padding: 1.5rem; border-radius: 1rem; margin-bottom: 1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 0.5rem; font-size: 1rem; }
.voice-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }
.voice-card { border: 2px solid #eee; border-radius: 0.5rem; padding: 1rem; text-align: center; cursor: pointer; transition: all 0.3s; }
.voice-card:hover { border-color: #667eea; transform: translateY(-2px); }
.voice-card.selected { border-color: #667eea; background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); }
.voice-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.voice-name { font-weight: bold; margin-bottom: 0.25rem; }
.voice-style { color: #999; font-size: 0.85rem; }
.btn-clone { width: 100%; padding: 1rem; font-size: 1.1rem; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 0.5rem; cursor: pointer; }
.btn-clone:disabled { opacity: 0.5; cursor: not-allowed; }
.result h3 { margin-bottom: 1rem; }
.btn-download { display: inline-block; margin-top: 1rem; padding: 0.75rem 2rem; background: #388e3c; color: white; text-decoration: none; border-radius: 0.5rem; }
</style>
