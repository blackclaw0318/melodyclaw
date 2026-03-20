<template>
  <div
    class="lobster-container absolute cursor-move select-none touch-none"
    :style="containerStyle"
    @mousedown="startDrag"
    @touchstart="startDrag"
  >
    <svg viewBox="0 0 300 280" class="w-32 h-32 drop-shadow-lg" :class="{ playing: isPlaying }">
      <!-- 身体 -->
      <ellipse class="body transition-all" cx="150" cy="180" rx="60" ry="40" :fill="colors.body" />
      
      <!-- 头部 -->
      <circle class="head transition-all" cx="150" cy="120" r="40" :fill="colors.head" />
      
      <!-- 眼睛 -->
      <g class="eyes">
        <circle cx="135" cy="110" r="8" fill="white" />
        <circle cx="165" cy="110" r="8" fill="white" />
        <circle cx="137" cy="112" r="4" fill="#333" />
        <circle cx="167" cy="112" r="4" fill="#333" />
      </g>
      
      <!-- 钳子 -->
      <g 
        class="claw left-claw" 
        :style="{ transformOrigin: '150px 160px', transform: `rotate(${playing ? clawAngle : -20}deg)` }"
      >
        <path d="M 100 160 L 70 140 L 75 170 Z" :fill="colors.claw" stroke="#ff5252" stroke-width="2" />
      </g>
      
      <g 
        class="claw right-claw" 
        :style="{ transformOrigin: '150px 160px', transform: `rotate(${playing ? -clawAngle : 20}deg)` }"
      >
        <path d="M 200 160 L 230 140 L 225 170 Z" :fill="colors.claw" stroke="#ff5252" stroke-width="2" />
      </g>
      
      <!-- 触须 -->
      <g class="antennae">
        <path d="M 130 85 Q 120 60 110 50" stroke="#ff6b6b" stroke-width="3" fill="none" />
        <path d="M 170 85 Q 180 60 190 50" stroke="#ff6b6b" stroke-width="3" fill="none" />
        <circle cx="110" cy="50" r="5" fill="#ff6b6b" />
        <circle cx="190" cy="50" r="5" fill="#ff6b6b" />
      </g>
      
      <!-- 尾巴 -->
      <path d="M 150 220 L 130 250 L 150 240 L 170 250 Z" fill="#ff6b6b" />
      
      <!-- 音符 -->
      <g v-if="playing" class="notes">
        <text x="80" y="80" fill="#667eea" font-size="24" :style="{ opacity: note1Opacity }">♪</text>
        <text x="220" y="60" fill="#667eea" font-size="24" :style="{ opacity: note2Opacity }">♫</text>
        <text x="90" y="50" fill="#764ba2" font-size="20" :style="{ opacity: note3Opacity }">♬</text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDraggable } from '@/composables/useDraggable'

const props = defineProps({
  isPlaying: { type: Boolean, default: false },
  initialPosition: { type: Object, default: () => ({ x: 100, y: 100 }) },
  locked: { type: Boolean, default: false },
  colors: { 
    type: Object, 
    default: () => ({ body: '#ff6b6b', head: '#ff8787', claw: '#ff6b6b' })
  }
})

const emit = defineEmits(['position-change'])

const clawAngle = ref(-20)
const note1Opacity = ref(0)
const note2Opacity = ref(0)
const note3Opacity = ref(0)

const { x, y, isDragging, startDrag, endDrag } = useDraggable({
  initialX: props.initialPosition.x,
  initialY: props.initialPosition.y,
  onDrag: (pos) => emit('position-change', pos)
})

const containerStyle = computed(() => ({
  transform: `translate(${x.value}px, ${y.value}px)`,
  cursor: props.locked ? 'default' : (isDragging.value ? 'grabbing' : 'grab'),
  pointerEvents: props.locked ? 'none' : 'auto',
  transition: isDragging.value ? 'none' : 'transform 0.1s ease'
}))

// 动画循环
let animationId = null

onMounted(() => {
  const animate = () => {
    if (props.isPlaying) {
      const time = Date.now() / 500
      clawAngle.value = Math.sin(time) * 20
      note1Opacity.value = 0.5 + Math.sin(time) * 0.5
      note2Opacity.value = 0.5 + Math.cos(time) * 0.5
      note3Opacity.value = 0.3 + Math.sin(time + 2) * 0.4
    }
    animationId = requestAnimationFrame(animate)
  }
  animate()
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

<style scoped>
.claw {
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
</style>
