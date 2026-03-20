import axios from 'axios'

// 后端 API 地址（根据部署环境配置）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://111.228.46.221:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可在此添加 token
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api
