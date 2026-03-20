import { ref } from 'vue'

/**
 * 拖拽功能 Hook
 * @param {Object} options - 配置选项
 * @param {number} options.initialX - 初始 X 坐标
 * @param {number} options.initialY - 初始 Y 坐标
 * @param {Function} options.onDrag - 拖拽时的回调函数
 */
export function useDraggable(options = {}) {
  const {
    initialX = 0,
    initialY = 0,
    onDrag = null
  } = options

  const x = ref(initialX)
  const y = ref(initialY)
  const isDragging = ref(false)
  const startX = ref(0)
  const startY = ref(0)
  const startElemX = ref(0)
  const startElemY = ref(0)

  /**
   * 开始拖拽
   */
  function startDrag(event) {
    isDragging.value = true
    
    const clientX = event.touches ? event.touches[0].clientX : event.clientX
    const clientY = event.touches ? event.touches[0].clientY : event.clientY
    
    startX.value = clientX
    startY.value = clientY
    startElemX.value = x.value
    startElemY.value = y.value

    // 添加事件监听
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', endDrag)
    document.addEventListener('touchmove', onMove, { passive: false })
    document.addEventListener('touchend', endDrag)
  }

  /**
   * 拖拽中
   */
  function onMove(event) {
    if (!isDragging.value) return
    event.preventDefault()

    const clientX = event.touches ? event.touches[0].clientX : event.clientX
    const clientY = event.touches ? event.touches[0].clientY : event.clientY

    const deltaX = clientX - startX.value
    const deltaY = clientY - startY.value

    x.value = startElemX.value + deltaX
    y.value = startElemY.value + deltaY

    if (onDrag) {
      onDrag({ x: x.value, y: y.value })
    }
  }

  /**
   * 结束拖拽
   */
  function endDrag() {
    isDragging.value = false
    
    // 移除事件监听
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', endDrag)
    document.removeEventListener('touchmove', onMove)
    document.removeEventListener('touchend', endDrag)
  }

  return {
    x,
    y,
    isDragging,
    startDrag,
    endDrag
  }
}
