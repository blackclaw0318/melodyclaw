# MelodyClaw V2.0 - 技术框架设计文档

> 版本：2.0 | 日期：2026-03-19 | 状态：草案

---

## 1. 系统架构总览

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   iOS Safari │ │ Android Chrome│ │ Desktop Chrome│          │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Vue3)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  页面层 (Views)                                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │ Home    │ │ Record  │ │ Preview │ │ Profile │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  组件层 (Components)                                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Camera   │ │ Lobster  │ │ Lyrics   │ │ Recorder │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  服务层 (Services)                                       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Camera   │ │ Audio    │ │ Video    │ │ API      │  │   │
│  │  │ Service  │ │ Service  │ │ Service  │ │ Client   │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端层 (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  API Routes                                              │   │
│  │  /api/v2/songs  /api/v2/recordings  /api/v2/users       │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Business Logic                                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                │   │
│  │  │ Song     │ │ Recording│ │ Video    │                │   │
│  │  │ Service  │ │ Service  │ │ Service  │                │   │
│  │  └──────────┘ └──────────┘ └──────────┘                │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Data Access                                             │   │
│  │  ┌──────────┐ ┌──────────┐                              │   │
│  │  │ Database │ │ File     │                              │   │
│  │  │ (SQLite) │ │ Storage  │                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        基础设施层                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  FFmpeg     │ │  Nginx      │ │  Cloud      │               │
│  │  (转码)     │ │  (CDN)      │ │  Storage    │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 前端详细设计

### 2.1 项目结构

```
melodyclaw/frontend/
├── public/
│   ├── assets/
│   │   ├── lobster/          # 小龙虾动画帧序列
│   │   │   ├── frame_001.png
│   │   │   ├── frame_002.png
│   │   │   └── ...
│   │   └── covers/           # 默认歌曲封面
│   └── favicon.ico
├── src/
│   ├── api/
│   │   ├── index.js          # API 客户端配置
│   │   ├── songs.js          # 歌曲相关 API
│   │   ├── recordings.js     # 作品相关 API
│   │   └── users.js          # 用户相关 API
│   ├── assets/
│   │   ├── styles/
│   │   │   ├── main.css      # 全局样式
│   │   │   └── variables.css # CSS 变量
│   │   └── images/
│   ├── components/
│   │   ├── camera/
│   │   │   ├── CameraView.vue      # 摄像头视图
│   │   │   └── CameraSwitcher.vue  # 摄像头切换
│   │   ├── lobster/
│   │   │   ├── LobsterAnimation.vue # 小龙虾动画
│   │   │   └── LobsterSprite.vue   # 精灵渲染
│   │   ├── lyrics/
│   │   │   ├── LyricsScroll.vue    # 滚动歌词
│   │   │   └── LyricsLine.vue      # 单行歌词
│   │   ├── recorder/
│   │   │   ├── Recorder.vue        # 录制控制器
│   │   │   ├── Countdown.vue       # 倒计时动画
│   │   │   └── Timer.vue           # 录制计时器
│   │   ├── player/
│   │   │   ├── AudioPlayer.vue     # 音频播放器
│   │   │   └── VideoPlayer.vue     # 视频播放器
│   │   └── common/
│   │       ├── SongCard.vue        # 歌曲卡片
│   │       ├── LoadingSpinner.vue  # 加载动画
│   │       └── Modal.vue           # 弹窗组件
│   ├── composables/
│   │   ├── useCamera.js        # 摄像头 Hook
│   │   ├── useAudio.js         # 音频处理 Hook
│   │   ├── useRecorder.js      # 录制逻辑 Hook
│   │   ├── useDraggable.js     # 拖拽逻辑 Hook
│   │   └── useBPM.js           # BPM 计算 Hook
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── songs.js          # 歌曲状态
│   │   ├── recordings.js     # 作品状态
│   │   └── user.js           # 用户状态
│   ├── views/
│   │   ├── Home.vue          # 首页（歌曲列表）
│   │   ├── Record.vue        # 拍摄页面
│   │   ├── Preview.vue       # 预览页面
│   │   └── Profile.vue       # 个人中心
│   ├── utils/
│   │   ├── audio.js          # 音频工具函数
│   │   ├── video.js          # 视频工具函数
│   │   └── format.js         # 格式化工具
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

### 2.2 核心组件详细设计

#### 2.2.1 CameraView.vue

```vue
<template>
  <div class="camera-view relative w-full h-full overflow-hidden">
    <!-- 摄像头视频流 -->
    <video
      ref="videoRef"
      class="absolute inset-0 w-full h-full object-cover"
      autoplay
      playsinline
      muted
    />
    
    <!-- 叠加画布（小龙虾、歌词） -->
    <canvas
      ref="canvasRef"
      class="absolute inset-0 w-full h-full pointer-events-none"
    />
    
    <!-- 交互层（可拖动元素） -->
    <div class="absolute inset-0 z-10">
      <slot name="overlay" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useCamera } from '@/composables/useCamera'

const props = defineProps({
  facingMode: { type: String, default: 'user' }, // 'user' | 'environment'
  resolution: { type: String, default: '720p' }  // '720p' | '1080p'
})

const emit = defineEmits(['stream-ready', 'error'])

const videoRef = ref(null)
const canvasRef = ref(null)

const { 
  stream, 
  error, 
  startCamera, 
  stopCamera, 
  switchCamera 
} = useCamera()

onMounted(async () => {
  try {
    await startCamera(props.facingMode, props.resolution)
    if (videoRef.value && stream.value) {
      videoRef.value.srcObject = stream.value
      emit('stream-ready', stream.value)
    }
  } catch (err) {
    emit('error', err)
  }
})

onUnmounted(() => {
  stopCamera()
})

defineExpose({
  switchCamera,
  getStream: () => stream.value,
  captureFrame: () => {
    if (!canvasRef.value || !videoRef.value) return null
    const ctx = canvasRef.value.getContext('2d')
    canvasRef.value.width = videoRef.value.videoWidth
    canvasRef.value.height = videoRef.value.videoHeight
    ctx.drawImage(videoRef.value, 0, 0)
    return canvasRef.value.toDataURL('image/png')
  }
})
</script>
```

#### 2.2.2 useCamera.js (Composable)

```javascript
// src/composables/useCamera.js
import { ref, shallowRef } from 'vue'

export function useCamera() {
  const stream = shallowRef(null)
  const error = ref(null)
  const isOn = ref(false)

  const RESOLUTIONS = {
    '720p': { width: { ideal: 1280 }, height: { ideal: 720 } },
    '1080p': { width: { ideal: 1920 }, height: { ideal: 1080 } }
  }

  async function startCamera(facingMode = 'user', resolution = '720p') {
    try {
      if (stream.value) {
        stopCamera()
      }

      const constraints = {
        video: {
          facingMode,
          ...RESOLUTIONS[resolution]
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      }

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
      stream.value = mediaStream
      isOn.value = true
      error.value = null
      
      return mediaStream
    } catch (err) {
      error.value = err
      throw err
    }
  }

  function stopCamera() {
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
      stream.value = null
      isOn.value = false
    }
  }

  async function switchCamera() {
    const currentFacingMode = stream.value
      ? stream.value.getVideoTracks()[0].getSettings().facingMode
      : 'user'
    
    const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user'
    return await startCamera(newFacingMode)
  }

  return {
    stream,
    error,
    isOn,
    startCamera,
    stopCamera,
    switchCamera
  }
}
```

#### 2.2.3 LobsterAnimation.vue

```vue
<template>
  <div
    class="lobster-container absolute cursor-move select-none"
    :style="containerStyle"
    @mousedown="startDrag"
    @touchstart="startDrag"
  >
    <img
      :src="currentFrame"
      class="w-32 h-32 pointer-events-none"
      draggable="false"
      alt="lobster"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDraggable } from '@/composables/useDraggable'

const props = defineProps({
  frames: { type: Array, required: true },
  fps: { type: Number, default: 12 },
  isPlaying: { type: Boolean, default: false },
  initialPosition: { type: Object, default: () => ({ x: 50, y: 50 }) },
  locked: { type: Boolean, default: false }
})

const emit = defineEmits(['position-change'])

const currentFrameIndex = ref(0)
const containerRef = ref(null)

const { x, y, isDragging, startDrag, endDrag } = useDraggable({
  initialX: props.initialPosition.x,
  initialY: props.initialPosition.y,
  onDrag: (pos) => emit('position-change', pos)
})

const currentFrame = computed(() => 
  props.frames[currentFrameIndex.value]
)

const containerStyle = computed(() => ({
  transform: `translate(${x.value}px, ${y.value}px)`,
  cursor: props.locked ? 'default' : 'move',
  pointerEvents: props.locked ? 'none' : 'auto'
}))

// 动画帧循环
let animationId = null
let lastTime = 0
const frameInterval = 1000 / props.fps

function animate(timestamp) {
  if (!lastTime) lastTime = timestamp
  const elapsed = timestamp - lastTime

  if (elapsed > frameInterval && props.isPlaying) {
    currentFrameIndex.value = (currentFrameIndex.value + 1) % props.frames.length
    lastTime = timestamp
  }

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  animationId = requestAnimationFrame(animate)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  endDrag()
})

defineExpose({
  getPosition: () => ({ x: x.value, y: y.value }),
  setPosition: (pos) => {
    x.value = pos.x
    y.value = pos.y
  }
})
</script>
```

#### 2.2.4 useRecorder.js (录制核心逻辑)

```javascript
// src/composables/useRecorder.js
import { ref, shallowRef } from 'vue'
import { useAudio } from './useAudio'

export function useRecorder() {
  const isRecording = ref(false)
  const isPaused = ref(false)
  const recordingTime = ref(0)
  const recordedChunks = shallowRef([])
  const mediaRecorder = shallowRef(null)
  const error = ref(null)

  const { playAudio, pauseAudio, stopAudio, audioContext } = useAudio()

  let timerInterval = null
  let startTime = 0

  async function startRecording({ 
    cameraStream, 
    accompanimentUrl, 
    countdown = 3,
    onCountdown 
  }) {
    try {
      // 1. 倒计时
      for (let i = countdown; i > 0; i--) {
        if (onCountdown) onCountdown(i)
        await new Promise(resolve => setTimeout(resolve, 1000))
      }

      // 2. 创建 MediaRecorder
      const combinedStream = new MediaStream([
        ...cameraStream.getVideoTracks(),
        ...cameraStream.getAudioTracks()
      ])

      const recorder = new MediaRecorder(combinedStream, {
        mimeType: 'video/webm;codecs=vp9,opus',
        videoBitsPerSecond: 2500000 // 2.5 Mbps
      })

      recordedChunks.value = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.value.push(event.data)
        }
      }

      recorder.onstop = () => {
        isRecording.value = false
        clearInterval(timerInterval)
      }

      // 3. 开始录制
      recorder.start(1000) // 每秒生成一个 chunk
      mediaRecorder.value = recorder

      // 4. 播放伴奏
      await playAudio(accompanimentUrl)

      // 5. 开始计时
      isRecording.value = true
      startTime = Date.now()
      recordingTime.value = 0
      timerInterval = setInterval(() => {
        recordingTime.value = (Date.now() - startTime) / 1000
      }, 100)

      return true
    } catch (err) {
      error.value = err
      throw err
    }
  }

  function stopRecording() {
    if (mediaRecorder.value && isRecording.value) {
      mediaRecorder.value.stop()
      stopAudio()
    }
  }

  function pauseRecording() {
    if (mediaRecorder.value && isRecording.value && !isPaused.value) {
      mediaRecorder.value.pause()
      pauseAudio()
      clearInterval(timerInterval)
      isPaused.value = true
    }
  }

  function resumeRecording() {
    if (mediaRecorder.value && isRecording.value && isPaused.value) {
      mediaRecorder.value.resume()
      playAudio() // 需要恢复伴奏播放
      startTime = Date.now() - recordingTime.value * 1000
      timerInterval = setInterval(() => {
        recordingTime.value = (Date.now() - startTime) / 1000
      }, 100)
      isPaused.value = false
    }
  }

  function getRecordedBlob() {
    return new Blob(recordedChunks.value, { type: 'video/webm' })
  }

  function getRecordedURL() {
    const blob = getRecordedBlob()
    return URL.createObjectURL(blob)
  }

  return {
    isRecording,
    isPaused,
    recordingTime,
    error,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    getRecordedBlob,
    getRecordedURL
  }
}
```

### 2.3 页面路由设计

```javascript
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Record from '@/views/Record.vue'
import Preview from '@/views/Preview.vue'
import Profile from '@/views/Profile.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'MelodyClaw - 首页' }
  },
  {
    path: '/record/:songId',
    name: 'Record',
    component: Record,
    meta: { title: '拍摄 - MelodyClaw' },
    props: true
  },
  {
    path: '/preview/:recordingId',
    name: 'Preview',
    component: Preview,
    meta: { title: '预览 - MelodyClaw' },
    props: true
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { title: '我的 - MelodyClaw' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'MelodyClaw'
  next()
})

export default router
```

---

## 3. 后端详细设计

### 3.1 API 端点设计

#### 3.1.1 歌曲相关

```yaml
GET /api/v2/songs:
  summary: 获取歌曲列表
  parameters:
    - name: page
      in: query
      schema: { type: integer, default: 1 }
    - name: page_size
      in: query
      schema: { type: integer, default: 20 }
    - name: keyword
      in: query
      schema: { type: string }
    - name: category
      in: query
      schema: { type: string }
  responses:
    200:
      content:
        application/json:
          schema:
            type: object
            properties:
              songs:
                type: array
                items: { $ref: '#/components/schemas/Song' }
              total: { type: integer }

GET /api/v2/songs/{song_id}:
  summary: 获取歌曲详情
  responses:
    200:
      content:
        application/json:
          schema: { $ref: '#/components/schemas/SongDetail' }

GET /api/v2/songs/{song_id}/accompaniment:
  summary: 获取伴奏音频
  responses:
    200:
      content:
        audio/wav: { schema: { type: string, format: binary } }

GET /api/v2/songs/{song_id}/lyrics:
  summary: 获取歌词
  responses:
    200:
      content:
        application/json:
          schema:
            type: array
            items:
              type: object
              properties:
                time: { type: number }
                text: { type: string }
```

#### 3.1.2 作品相关

```yaml
POST /api/v2/recordings:
  summary: 上传录制作品
  requestBody:
    content:
      multipart/form-data:
        schema:
          type: object
          properties:
            song_id: { type: integer }
            video: { type: string, format: binary }
            lobster_position: { type: string }  # JSON string
            lyrics_position: { type: string }   # JSON string
  responses:
    201:
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Recording' }

GET /api/v2/recordings/{recording_id}:
  summary: 获取作品详情
  responses:
    200:
      content:
        application/json:
          schema: { $ref: '#/components/schemas/RecordingDetail' }

GET /api/v2/recordings/{recording_id}/video:
  summary: 下载作品视频
  responses:
    200:
      content:
        video/mp4: { schema: { type: string, format: binary } }

DELETE /api/v2/recordings/{recording_id}:
  summary: 删除作品
  responses:
    204: { description: 删除成功 }
```

### 3.2 数据库模型

```python
# backend/app/models_v2.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class SongV2(Base):
    """歌曲表 V2"""
    __tablename__ = "songs_v2"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=True)
    cover_file = Column(String(512), nullable=True)  # 封面图
    bpm = Column(Integer, nullable=True)  # BPM
    duration = Column(Float, nullable=True)
    original_file = Column(String(512), nullable=True)  # 原唱
    accompaniment_file = Column(String(512), nullable=True)  # 伴奏
    lyrics = Column(Text, nullable=True)  # 歌词 (JSON)
    category = Column(String(64), nullable=True)  # 分类
    duet_count = Column(Integer, default=0)  # 合唱次数
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联作品
    recordings = relationship("RecordingV2", back_populates="song")


class RecordingV2(Base):
    """录制作品表"""
    __tablename__ = "recordings_v2"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(64), unique=True, nullable=False, index=True)
    song_id = Column(Integer, ForeignKey("songs_v2.id"), nullable=False)
    user_id = Column(Integer, nullable=True)  # P2: 用户系统
    
    video_file = Column(String(512), nullable=False)
    thumbnail_file = Column(String(512), nullable=True)
    duration = Column(Float, nullable=True)
    
    # 位置信息
    lobster_position = Column(JSON, nullable=True)  # {x, y}
    lyrics_position = Column(JSON, nullable=True)   # {x, y}
    
    # 统计
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    song = relationship("SongV2", back_populates="recordings")


class UserV2(Base):
    """用户表 (P2)"""
    __tablename__ = "users_v2"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    avatar_file = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recordings = relationship("RecordingV2", back_populates="user")
```

### 3.3 视频处理服务

```python
# backend/services/video_processor.py
import subprocess
import os
from pathlib import Path

class VideoProcessor:
    """视频处理服务"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def convert_to_mp4(self, input_path: str, output_filename: str = None) -> str:
        """将 WebM 转换为 MP4 (H.264 + AAC)"""
        if not output_filename:
            output_filename = f"{Path(input_path).stem}.mp4"
        
        output_path = self.output_dir / output_filename
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)
    
    def generate_thumbnail(self, video_path: str, output_filename: str = None) -> str:
        """生成视频缩略图"""
        if not output_filename:
            output_filename = f"{Path(video_path).stem}.jpg"
        
        output_path = self.output_dir / output_filename
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:01',  # 第 1 秒
            '-vframes', '1',
            '-vf', 'scale=320:-1',
            '-y',
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)
    
    def get_video_info(self, video_path: str) -> dict:
        """获取视频信息"""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
```

---

## 4. 部署架构

### 4.1 Docker Compose 配置

```yaml
# docker-compose.v2.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=/api

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - melodyclaw-data:/app/data
      - melodyclaw-uploads:/app/uploads
    environment:
      - DATABASE_URL=sqlite:///./melodyclaw.db
      - UPLOAD_DIR=/app/uploads
    deploy:
      resources:
        limits:
          memory: 4G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - melodyclaw-data:/data
    depends_on:
      - frontend
      - backend

volumes:
  melodyclaw-data:
  melodyclaw-uploads:
```

### 4.2 Nginx 配置

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API 代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 视频上传大小限制
        client_max_body_size 500M;
        
        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # 视频文件静态服务
    location /videos {
        alias /data/videos;
        add_header Cache-Control "public, max-age=31536000";
        add_header Accept-Ranges bytes;
    }
}
```

---

## 5. 安全与权限

### 5.1 CORS 配置

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://melodyclaw.com",
        "https://www.melodyclaw.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 5.2 文件上传安全

```python
# backend/app/utils/security.py
import os
import uuid
from pathlib import Path

ALLOWED_VIDEO_EXTENSIONS = {'.webm', '.mp4', '.mov'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

def validate_file(filename: str, file_size: int, allowed_extensions: set) -> bool:
    """验证文件"""
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        return False
    if file_size > MAX_FILE_SIZE:
        return False
    return True

def generate_safe_filename(original_filename: str) -> str:
    """生成安全文件名"""
    ext = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"
```

---

## 6. 性能优化

### 6.1 前端优化

| 优化项 | 方案 | 预期效果 |
|--------|------|----------|
| 图片懒加载 | Intersection Observer | 减少首屏加载 |
| 视频分片上传 | 分片 + 断点续传 | 提升大文件上传稳定性 |
| 动画优化 | requestAnimationFrame + Canvas | 60fps 流畅动画 |
| 代码分割 | Vue Router 懒加载 | 减少初始包体积 |
| 缓存策略 | Service Worker | 离线可用 |

### 6.2 后端优化

| 优化项 | 方案 | 预期效果 |
|--------|------|----------|
| 视频转码异步 | Celery 任务队列 | 不阻塞 API 响应 |
| 文件 CDN | 云存储 + CDN | 加速视频分发 |
| 数据库索引 | 关键字段索引 | 查询性能提升 |
| 响应缓存 | Redis 缓存 | 减少重复计算 |

---

## 7. 测试策略

### 7.1 单元测试

```javascript
// frontend/tests/components/LobsterAnimation.test.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LobsterAnimation from '@/components/lobster/LobsterAnimation.vue'

describe('LobsterAnimation', () => {
  it('renders correctly', () => {
    const wrapper = mount(LobsterAnimation, {
      props: {
        frames: ['frame1.png', 'frame2.png'],
        fps: 12
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('emits position-change on drag', async () => {
    // ... 测试拖拽逻辑
  })
})
```

### 7.2 E2E 测试

```javascript
// tests/e2e/recording.spec.js
import { test, expect } from '@playwright/test'

test('complete recording flow', async ({ page }) => {
  // 1. 打开首页
  await page.goto('/')
  
  // 2. 选择歌曲
  await page.click('[data-testid="song-card-1"]')
  
  // 3. 进入拍摄页面
  await expect(page).toHaveURL(/\/record\/\d+/)
  
  // 4. 允许摄像头权限
  // ...
  
  // 5. 点击录制
  await page.click('[data-testid="record-button"]')
  
  // 6. 等待倒计时
  await expect(page.locator('[data-testid="countdown"]')).toBeVisible()
  
  // 7. 录制中
  await expect(page.locator('[data-testid="recording-timer"]')).toBeVisible()
  
  // 8. 停止录制
  await page.click('[data-testid="stop-button"]')
  
  // 9. 跳转到预览
  await expect(page).toHaveURL(/\/preview\/\d+/)
})
```

---

## 8. 监控与日志

### 8.1 前端监控

```javascript
// src/utils/analytics.js
export function trackEvent(eventName, properties = {}) {
  // 发送到分析服务
  fetch('/api/v2/analytics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event: eventName,
      properties,
      timestamp: Date.now()
    })
  })
}

// 使用示例
trackEvent('recording_started', { songId: 1 })
trackEvent('recording_completed', { duration: 180 })
```

### 8.2 后端日志

```python
# backend/app/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    handler = RotatingFileHandler(
        'logs/melodyclaw.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('melodyclaw')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
```

---

**文档状态**：待评审  
**下一步**：开发实施
