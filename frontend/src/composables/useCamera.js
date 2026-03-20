import { ref, shallowRef } from 'vue'

/**
 * 摄像头控制 Hook
 * @returns {Object} 摄像头控制方法
 */
export function useCamera() {
  const stream = shallowRef(null)
  const error = ref(null)
  const isOn = ref(false)
  const facingMode = ref('environment') // 默认后置摄像头

  const RESOLUTIONS = {
    '720p': { width: { ideal: 1280 }, height: { ideal: 720 } },
    '1080p': { width: { ideal: 1920 }, height: { ideal: 1080 } }
  }

  /**
   * 启动摄像头
   * @param {string} mode - 'user' | 'environment'
   * @param {string} resolution - '720p' | '1080p'
   */
  async function startCamera(mode = 'environment', resolution = '720p') {
    try {
      if (stream.value) {
        stopCamera()
      }

      const constraints = {
        video: {
          facingMode: mode,
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
      facingMode.value = mode
      isOn.value = true
      error.value = null
      
      return mediaStream
    } catch (err) {
      error.value = err
      console.error('摄像头启动失败:', err)
      throw err
    }
  }

  /**
   * 停止摄像头
   */
  function stopCamera() {
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
      stream.value = null
      isOn.value = false
    }
  }

  /**
   * 切换摄像头
   */
  async function switchCamera() {
    const newMode = facingMode.value === 'user' ? 'environment' : 'user'
    await startCamera(newMode)
    return newMode
  }

  return {
    stream,
    error,
    isOn,
    facingMode,
    startCamera,
    stopCamera,
    switchCamera
  }
}
