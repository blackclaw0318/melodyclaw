import { ref, shallowRef } from 'vue'

/**
 * 录制功能 Hook
 */
export function useRecorder() {
  const isRecording = ref(false)
  const isPaused = ref(false)
  const recordingTime = ref(0)
  const recordedChunks = shallowRef([])
  const mediaRecorder = shallowRef(null)
  const error = ref(null)

  let timerInterval = null
  let startTime = 0

  /**
   * 开始录制
   * @param {Object} options - 录制配置
   * @param {MediaStream} options.cameraStream - 摄像头流
   * @param {string} options.accompanimentUrl - 伴奏 URL
   * @param {Function} options.onProgress - 进度回调
   */
  async function startRecording({ 
    cameraStream, 
    accompanimentUrl = null,
    onProgress = null 
  }) {
    try {
      // 创建录制流（视频 + 麦克风）
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
        if (timerInterval) {
          clearInterval(timerInterval)
        }
      }

      // 开始录制
      recorder.start(1000) // 每秒生成一个 chunk
      mediaRecorder.value = recorder

      // 播放伴奏（如果有）
      let audioElement = null
      if (accompanimentUrl) {
        audioElement = new Audio(accompanimentUrl)
        audioElement.play()
      }

      // 开始计时
      isRecording.value = true
      startTime = Date.now()
      recordingTime.value = 0
      
      timerInterval = setInterval(() => {
        recordingTime.value = (Date.now() - startTime) / 1000
        if (onProgress) {
          onProgress(recordingTime.value)
        }
      }, 100)

      return { recorder, audioElement }
    } catch (err) {
      error.value = err
      console.error('录制启动失败:', err)
      throw err
    }
  }

  /**
   * 停止录制
   */
  function stopRecording() {
    if (mediaRecorder.value && isRecording.value) {
      mediaRecorder.value.stop()
      mediaRecorder.value = null
    }
  }

  /**
   * 暂停录制
   */
  function pauseRecording() {
    if (mediaRecorder.value && isRecording.value && !isPaused.value) {
      mediaRecorder.value.pause()
      clearInterval(timerInterval)
      isPaused.value = true
    }
  }

  /**
   * 恢复录制
   */
  function resumeRecording() {
    if (mediaRecorder.value && isRecording.value && isPaused.value) {
      mediaRecorder.value.resume()
      startTime = Date.now() - recordingTime.value * 1000
      timerInterval = setInterval(() => {
        recordingTime.value = (Date.now() - startTime) / 1000
      }, 100)
      isPaused.value = false
    }
  }

  /**
   * 获取录制的 Blob
   */
  function getRecordedBlob() {
    return new Blob(recordedChunks.value, { type: 'video/webm' })
  }

  /**
   * 获取录制的 URL
   */
  function getRecordedURL() {
    const blob = getRecordedBlob()
    return URL.createObjectURL(blob)
  }

  /**
   * 格式化录制时间
   */
  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
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
    getRecordedURL,
    formatTime
  }
}
