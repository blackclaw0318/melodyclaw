import api from './index'

/**
 * 作品相关 API（V2 新增）
 */
export const recordingsApi = {
  /**
   * 上传录制作品
   * @param {FormData} formData - 包含视频文件、歌曲 ID、位置信息的 FormData
   */
  upload(formData) {
    return api.post('/api/v2/recordings', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  /**
   * 获取作品详情
   * @param {number} id - 作品 ID
   */
  getById(id) {
    return api.get(`/api/v2/recordings/${id}`)
  },

  /**
   * 获取作品视频
   * @param {number} id - 作品 ID
   */
  async getVideo(id) {
    const response = await api.get(`/api/v2/recordings/${id}/video`, {
      responseType: 'blob'
    })
    return URL.createObjectURL(new Blob([response]))
  },

  /**
   * 删除作品
   * @param {number} id - 作品 ID
   */
  delete(id) {
    return api.delete(`/api/v2/recordings/${id}`)
  },

  /**
   * 获取作品列表
   * @param {Object} params - 查询参数
   */
  getList(params = {}) {
    return api.get('/api/v2/recordings', { params })
  },

  /**
   * 点赞作品
   * @param {number} id - 作品 ID
   */
  like(id) {
    return api.post(`/api/v2/recordings/${id}/like`)
  },

  /**
   * 增加播放次数
   * @param {number} id - 作品 ID
   */
  incrementView(id) {
    return api.post(`/api/v2/recordings/${id}/view`)
  }
}
