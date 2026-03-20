<template>
  <div class="recorder-controls flex items-center justify-center gap-6">
    <!-- 录制按钮 -->
    <button
      v-if="!isRecording"
      @click="handleRecord"
      class="record-btn w-20 h-20 rounded-full bg-red-500 border-4 border-red-300 shadow-lg hover:bg-red-600 active:scale-95 transition-all flex items-center justify-center"
      :disabled="isCountingDown"
    >
      <div class="w-16 h-16 rounded-full bg-white/20"></div>
    </button>
    
    <!-- 停止按钮 -->
    <button
      v-if="isRecording"
      @click="handleStop"
      class="stop-btn w-20 h-20 rounded-full bg-red-600 border-4 border-red-400 shadow-lg hover:bg-red-700 active:scale-95 transition-all flex items-center justify-center"
    >
      <div class="w-8 h-8 rounded bg-white"></div>
    </button>
  </div>
  
  <!-- 录制计时器 -->
  <div v-if="isRecording" class="recording-timer absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/60 backdrop-blur-md px-4 py-2 rounded-full">
    <div class="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
    <span class="text-white font-mono text-lg">{{ formattedTime }}</span>
  </div>
  
  <!-- 倒计时组件 -->
  <Countdown 
    v-if="isCountingDown"
    :duration="countdownDuration"
    :bpm="bpm"
    @complete="onCountdownComplete"
  />
</template>

<script setup>
import { ref, computed, defineEmits } from 'vue'
import Countdown from './Countdown.vue'

const props = defineProps({
  countdownDuration: { type: Number, default: 3 },
  bpm: { type: Number, default: 120 },
  maxDuration: { type: Number, default: 300 } // 最长录制 5 分钟
})

const emit = defineEmits(['start', 'stop', 'complete'])

const isRecording = ref(false)
const isCountingDown = ref(false)
const recordingTime = ref(0)
let timerInterval = null

const formattedTime = computed(() => {
  const mins = Math.floor(recordingTime.value / 60)
  const secs = Math.floor(recordingTime.value % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

function handleRecord() {
  isCountingDown.value = true
}

async function onCountdownComplete() {
  isCountingDown.value = false
  isRecording.value = true
  recordingTime.value = 0
  
  emit('start')
  
  // 开始计时
  timerInterval = setInterval(() => {
    recordingTime.value += 0.1
    
    // 检查是否超过最大时长
    if (recordingTime.value >= props.maxDuration) {
      handleStop()
    }
  }, 100)
}

function handleStop() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  
  isRecording.value = false
  emit('stop', recordingTime.value)
  emit('complete')
}

defineExpose({
  isRecording,
  recordingTime,
  stop: handleStop
})
</script>

<style scoped>
.record-btn {
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
}

.stop-btn {
  box-shadow: 0 4px 20px rgba(220, 38, 38, 0.4);
}
</style>
