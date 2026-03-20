<template>
  <div class="camera-view relative w-full h-full overflow-hidden bg-black">
    <!-- 摄像头视频流 -->
    <video
      ref="videoRef"
      class="absolute inset-0 w-full h-full object-cover"
      autoplay
      playsinline
      muted
    />
    
    <!-- 错误提示 -->
    <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-black/80 z-50">
      <div class="text-center text-white p-4">
        <p class="text-xl mb-2">⚠️ 摄像头启动失败</p>
        <p class="text-sm text-gray-400">{{ error.message }}</p>
        <button 
          @click="retry" 
          class="mt-4 px-4 py-2 bg-primary rounded-lg hover:bg-primary/80"
        >
          重试
        </button>
      </div>
    </div>
    
    <!-- 叠加层（歌词、小龙虾） -->
    <div class="absolute inset-0 z-10 pointer-events-none">
      <slot name="overlay" />
    </div>
    
    <!-- 交互层（可拖动元素） -->
    <div class="absolute inset-0 z-20">
      <slot name="interactive" />
    </div>
    
    <!-- 控制层 -->
    <div class="absolute bottom-0 left-0 right-0 z-30 p-4">
      <slot name="controls" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useCamera } from '@/composables/useCamera'

const props = defineProps({
  facingMode: { type: String, default: 'environment' },
  resolution: { type: String, default: '720p' }
})

const emit = defineEmits(['stream-ready', 'error', 'ready'])

const videoRef = ref(null)
const { stream, error, startCamera, stopCamera, switchCamera } = useCamera()

onMounted(async () => {
  await initCamera()
})

onUnmounted(() => {
  stopCamera()
})

async function initCamera() {
  try {
    await startCamera(props.facingMode, props.resolution)
    if (videoRef.value && stream.value) {
      videoRef.value.srcObject = stream.value
      emit('stream-ready', stream.value)
      emit('ready')
    }
  } catch (err) {
    emit('error', err)
  }
}

async function retry() {
  await initCamera()
}

defineExpose({
  switchCamera,
  getStream: () => stream.value,
  captureFrame: () => {
    if (!videoRef.value) return null
    const canvas = document.createElement('canvas')
    canvas.width = videoRef.value.videoWidth
    canvas.height = videoRef.value.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoRef.value, 0, 0)
    return canvas.toDataURL('image/png')
  }
})
</script>

<style scoped>
.camera-view {
  aspect-ratio: 9/16;
  max-height: 100%;
}
</style>
