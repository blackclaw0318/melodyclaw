import { defineStore } from 'pinia'
import axios from 'axios'

// 后端 API 地址
const API_BASE = 'http://111.228.46.221:8000/api/v1'

export const useSongStore = defineStore('song', {
  state: () => ({ songs: [], loading: false }),
  actions: {
    async fetchSongs() {
      this.loading = true
      const res = await axios.get(`${API_BASE}/songs`)
      this.songs = res.data
      this.loading = false
    },
    async uploadSong(file, title, artist) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', title)
      if (artist) formData.append('artist', artist)
      const res = await axios.post(`${API_BASE}/songs`, formData)
      this.fetchSongs()
      return res.data
    },
    async deleteSong(id) {
      await axios.delete(`${API_BASE}/songs/${id}`)
      this.fetchSongs()
    }
  }
})

export const useCloneStore = defineStore('clone', {
  state: () => ({ voices: [] }),
  actions: {
    async fetchVoices() {
      const res = await axios.get(`${API_BASE}/voices`)
      this.voices = res.data
    }
  }
})
