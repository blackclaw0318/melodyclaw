import { ref, computed } from 'vue'

/**
 * BPM 节奏控制 Hook
 */
export function useBPM() {
  const bpm = ref(120)
  const countdownDuration = ref(3)

  /**
   * 每拍时长（秒）
   */
  const beatDuration = computed(() => 60 / bpm.value)

  /**
   * 设置 BPM
   */
  function setBPM(value) {
    bpm.value = value
  }

  /**
   * 获取倒计时每拍的显示时间
   * @param {number} beatCount - 每数字持续几拍
   */
  function getCountdownBeatTime(beatCount = 2) {
    return beatDuration.value * beatCount
  }

  /**
   * 根据 BPM 计算倒计时总时长
   */
  function getTotalCountdownTime() {
    // 默认每数字持续 2 拍
    return countdownDuration.value * getCountdownBeatTime(2)
  }

  return {
    bpm,
    countdownDuration,
    beatDuration,
    setBPM,
    getCountdownBeatTime,
    getTotalCountdownTime
  }
}
