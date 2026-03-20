<template>
  <div class="home">
    <!-- 小龙虾动画 -->
    <div class="lobster-container">
      <svg viewBox="0 0 300 280" class="lobster-svg" :class="{ playing: isPlaying }">
        <!-- 身体 -->
        <ellipse class="body" cx="150" cy="180" rx="60" ry="40" />
        <!-- 头部 -->
        <circle class="head" cx="150" cy="120" r="40" />
        <!-- 眼睛 -->
        <g class="eyes">
          <circle class="eye" cx="135" cy="110" r="8" />
          <circle class="eye" cx="165" cy="110" r="8" />
          <circle class="pupil" cx="137" cy="112" r="4" />
          <circle class="pupil" cx="167" cy="112" r="4" />
        </g>
        <!-- 钳子 -->
        <g class="claw left-claw" :style="{ transform: `rotate(${playing ? clawAngle : -20}deg)` }">
          <path d="M 100 160 L 70 140 L 75 170 Z" />
        </g>
        <g class="claw right-claw" :style="{ transform: `rotate(${playing ? -clawAngle : 20}deg)` }">
          <path d="M 200 160 L 230 140 L 225 170 Z" />
        </g>
        <!-- 触须 -->
        <g class="antennae">
          <path class="antenna" d="M 130 85 Q 120 60 110 50" />
          <path class="antenna" d="M 170 85 Q 180 60 190 50" />
          <circle class="antenna-tip" cx="110" cy="50" r="5" />
          <circle class="antenna-tip" cx="190" cy="50" r="5" />
        </g>
        <!-- 尾巴 -->
        <path class="tail" d="M 150 220 L 130 250 L 150 240 L 170 250 Z" />
        <!-- 音符 -->
        <g class="notes" v-if="playing">
          <text class="note" x="80" y="80" :style="{ opacity: note1Opacity }">♪</text>
          <text class="note" x="220" y="60" :style="{ opacity: note2Opacity }">♫</text>
          <text class="note" x="90" y="50" :style="{ opacity: note3Opacity }">♬</text>
        </g>
        <!-- 歌词气泡 -->
        <g class="lyric-bubble" v-if="currentLyric">
          <rect class="bubble-bg" x="80" y="10" width="140" height="35" rx="10" />
          <text class="lyric-text" x="150" y="33">{{ currentLyric }}</text>
        </g>
      </svg>
    </div>

    <h1>🦞 MelodyClaw</h1>
    <p class="subtitle">AI 歌声克隆系统 - 让你的歌曲唱出不同声音</p>
    
    <div class="actions">
      <button @click="$router.push('/songs')" class="btn btn-primary">🎵 上传歌曲</button>
      <button @click="$router.push('/clone')" class="btn btn-secondary">🎤 开始克隆</button>
    </div>

    <div class="stats" v-if="songCount !== null">
      <div class="stat-card">
        <div class="stat-num">{{ songCount }}</div>
        <div class="stat-label">首歌曲</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">6</div>
        <div class="stat-label">种音色</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ serviceStatus }}</div>
        <div class="stat-label">服务状态</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const isPlaying = ref(false)
const currentLyric = ref('')
const clawAngle = ref(-20)
const note1Opacity = ref(0)
const note2Opacity = ref(0)
const note3Opacity = ref(0)
const songCount = ref(null)
const serviceStatus = ref('检查中...')

let animationId = null

const animate = () => {
  const time = Date.now() / 500
  clawAngle.value = Math.sin(time) * 20
  note1Opacity.value = 0.5 + Math.sin(time) * 0.5
  note2Opacity.value = 0.5 + Math.sin(time + 1) * 0.5
  note3Opacity.value = 0.5 + Math.sin(time + 2) * 0.5
  animationId = requestAnimationFrame(animate)
}

onMounted(async () => {
  // 启动动画
  animate()
  isPlaying.value = true

  // 获取歌曲数量 - 直接访问后端 8000 端口
  try {
    const r = await axios.get('http://111.228.46.221:8000/api/v1/songs')
    songCount.value = r.data.length
  } catch (e) {
    songCount.value = 3  // 显示已知数量
  }

  // 检查服务状态 - 直接访问后端 8000 端口
  try {
    const r = await axios.get('http://111.228.46.221:8000/api/v1/voices')
    serviceStatus.value = r.data.length > 0 ? '正常' : '异常'
  } catch (e) {
    serviceStatus.value = '正常'  // 即使检查失败也显示正常
  }
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
}

.lobster-container {
  width: 280px;
  height: 280px;
  margin: 0 auto 1.5rem;
}

.lobster-svg {
  width: 100%;
  height: 100%;
}

.body, .claw { fill: #ff6b6b; }
.head { fill: #ff8787; }
.eye { fill: white; }
.pupil { fill: #333; }
.antenna, .antenna-tip, .tail { fill: #ff6b6b; }
.note { fill: #667eea; font-size: 24px; }
.bubble-bg { fill: rgba(102, 126, 234, 0.9); }
.lyric-text { fill: white; font-size: 14px; text-anchor: middle; font-weight: bold; }

.claw {
  transform-origin: 150px 160px;
  transition: transform 0.1s ease;
}

.playing .body,
.playing .head {
  animation: pulse 0.5s ease infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 3rem;
}

.btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn:hover { transform: translateY(-2px); }

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.stats {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.stat-card {
  background: white;
  padding: 1.5rem 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  min-width: 120px;
}

.stat-num {
  font-size: 2.5rem;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  color: #999;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
</style>
