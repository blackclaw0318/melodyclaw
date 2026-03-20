import api from './index'

/**
 * 歌曲相关 API
 */
export const songsApi = {
  /**
   * 获取歌曲列表
   */
  getList(params = {}) {
    return api.get('/api/v1/songs', { params })
  },

  /**
   * 获取歌曲详情
   * @param {number} id - 歌曲 ID
   */
  getById(id) {
    return api.get(`/api/v1/songs/${id}`)
  },

  /**
   * 上传歌曲
   * @param {FormData} formData - 包含文件和元数据的 FormData
   */
  upload(formData) {
    return api.post('/api/v1/songs', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  /**
   * 删除歌曲
   * @param {number} id - 歌曲 ID
   */
  delete(id) {
    return api.delete(`/api/v1/songs/${id}`)
  },

  /**
   * 触发人声分离
   * @param {number} id - 歌曲 ID
   */
  separate(id) {
    return api.post(`/api/v1/songs/${id}/separate`)
  },

  /**
   * 歌词对齐
   * @param {number} songId - 歌曲 ID
   * @param {string} lyrics - 歌词文本
   */
  alignLyrics(songId, lyrics) {
    return api.post(`/api/v1/lyrics/${songId}/align`, { song_id: songId, lyrics })
  },

  /**
   * 获取伴奏音频（V2 新增）
   * @param {number} id - 歌曲 ID
   */
  async getAccompaniment(id) {
    const response = await api.get(`/api/v1/songs/${id}/accompaniment`, {
      responseType: 'blob'
    })
    return URL.createObjectURL(new Blob([response]))
  },

  /**
   * 获取歌词
   * @param {number} id - 歌曲 ID
   */
  getLyrics(id) {
    return api.get(`/api/v1/lyrics/${id}`)
  }
}
