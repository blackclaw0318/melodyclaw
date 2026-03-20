<template>
  <Teleport to="body">
    <transition 
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="isVisible" class="countdown-overlay fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <!-- 倒计时数字 -->
        <div 
          v-if="currentNumber > 0"
          class="countdown-number text-9xl md:text-[12rem] font-bold text-white animate-bounce drop-shadow-2xl"
          :key="currentNumber"
        >
          {{ currentNumber }}
        </div>
        
        <!-- 开始图标 -->
        <div v-else class="text-center">
          <div class="text-8xl mb-4 animate-pulse">🎤</div>
          <div class="text-2xl text-white font-light">开始演唱</div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, defineEmits } from 'vue'

const props = defineProps({
  duration: { type: Number, default: 3 },
  bpm: { type: Number, default: 120 }
})

const emit = defineEmits(['complete', 'tick'])

const isVisible = ref(true)
const currentNumber = ref(props.duration)

onMounted(async () => {
  // 根据 BPM 计算每拍时长
  const beatDuration = 60 / props.bpm * 1000 // 毫秒
  
  // 倒计时：每个数字持续 2 拍
  const numberDuration = beatDuration * 2
  
  for (let i = props.duration; i > 0; i--) {
    currentNumber.value = i
    emit('tick', i)
    
    // 等待当前数字显示完成
    await new Promise(resolve => setTimeout(resolve, numberDuration))
  }
  
  // 显示开始图标
  currentNumber.value = 0
  await new Promise(resolve => setTimeout(resolve, beatDuration))
  
  isVisible.value = false
  emit('complete')
})

// 暴露方法用于提前关闭
defineExpose({
  cancel: () => {
    isVisible.value = false
  }
})
</script>

<style scoped>
.animate-bounce {
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { 
    transform: scale(1) translateY(0);
  }
  50% { 
    transform: scale(1.2) translateY(-20px);
  }
}

.countdown-number {
  text-shadow: 0 0 40px rgba(102, 126, 234, 0.8);
}
</style>
