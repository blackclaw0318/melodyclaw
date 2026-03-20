<template>
  <div
    class="lyrics-container absolute pointer-events-auto"
    :style="containerStyle"
    @mousedown="startDrag"
    @touchstart="startDrag"
  >
    <div 
      class="lyrics-content bg-black/70 backdrop-blur-md rounded-xl p-4 shadow-2xl transition-all"
      :class="[
        maxWidthClass,
        { 'border border-white/20': isDragging }
      ]"
    >
      <!-- 拖拽手柄（仅在未锁定时显示） -->
      <div v-if="!locked" class="drag-handle text-center mb-2">
        <div class="w-8 h-1 bg-white/30 rounded-full mx-auto"></div>
      </div>
      
      <!-- 歌词内容 -->
      <div class="lyrics-scroll max-h-48 overflow-hidden">
        <div
          v-for="(line, index) in visibleLyrics"
          :key="index"
          class="lyric-line py-1.5 text-center transition-all duration-300 leading-relaxed"
          :class="{ 
            'text-white text-xl font-bold scale-110 drop-shadow-lg': currentIndex === index,
            'text-gray-400 text-base': currentIndex !== index
          }"
        >
          {{ line.text }}
        </div>
      </div>
      
      <!-- 无歌词提示 -->
      <div v-if="lyrics.length === 0" class="text-gray-500 text-center py-4">
        暂无歌词
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDraggable } from '@/composables/useDraggable'

const props = defineProps({
  lyrics: { type: Array, required: true, default: () => [] },
  currentIndex: { type: Number, default: -1 },
  initialPosition: { type: Object, default: () => ({ x: 50, y: 200 }) },
  locked: { type: Boolean, default: false },
  maxWidth: { type: String, default: 'md' } // 'sm' | 'md' | 'lg' | 'xl'
})

const emit = defineEmits(['position-change'])

const maxWidthClasses = {
  sm: 'max-w-xs',
  md: 'max-w-sm',
  lg: 'max-w-md',
  xl: 'max-w-lg'
}

const maxWidthClass = computed(() => maxWidthClasses[props.maxWidth] || maxWidthClasses.md)

// 显示当前歌词前后各 2 句
const visibleLyrics = computed(() => {
  if (props.lyrics.length <= 5) return props.lyrics
  
  const start = Math.max(0, props.currentIndex - 2)
  const end = Math.min(props.lyrics.length, props.currentIndex + 3)
  return props.lyrics.slice(start, end)
})

const { x, y, isDragging, startDrag, endDrag } = useDraggable({
  initialX: props.initialPosition.x,
  initialY: props.initialPosition.y,
  onDrag: (pos) => emit('position-change', pos)
})

const containerStyle = computed(() => ({
  transform: `translate(${x.value}px, ${y.value}px)`,
  cursor: props.locked ? 'default' : (isDragging.value ? 'grabbing' : 'grab'),
  pointerEvents: props.locked ? 'none' : 'auto'
}))

defineExpose({
  getPosition: () => ({ x: x.value, y: y.value }),
  setPosition: (pos) => {
    x.value = pos.x
    y.value = pos.y
  }
})
</script>

<style scoped>
.lyric-line {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.lyrics-scroll {
  mask-image: linear-gradient(
    to bottom,
    transparent 0%,
    black 15%,
    black 85%,
    transparent 100%
  );
  -webkit-mask-image: linear-gradient(
    to bottom,
    transparent 0%,
    black 15%,
    black 85%,
    transparent 100%
  );
}
</style>
