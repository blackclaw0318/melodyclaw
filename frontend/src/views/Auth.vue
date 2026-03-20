<template>
  <div class="auth-page min-h-screen bg-gradient-to-br from-primary to-secondary flex items-center justify-center p-4">
    <div class="auth-container bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
      <!-- 头部 -->
      <div class="auth-header bg-gradient-to-r from-primary/10 to-secondary/10 p-6 text-center">
        <h1 class="text-3xl font-bold text-primary mb-2">🦞 MelodyClaw</h1>
        <p class="text-gray-600">
          {{ isLogin ? '欢迎回来' : '创建你的账户' }}
        </p>
      </div>

      <!-- 表单 -->
      <div class="auth-body p-6">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- 用户名 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              v-model="form.username"
              type="text"
              required
              placeholder="请输入用户名"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
            />
          </div>

          <!-- 密码 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="form.password"
              type="password"
              required
              placeholder="请输入密码"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
            />
          </div>

          <!-- 确认密码（注册时显示） -->
          <div v-if="!isLogin">
            <label class="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
            <input
              v-model="form.confirmPassword"
              type="password"
              required
              placeholder="请再次输入密码"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
            />
          </div>

          <!-- 邮箱（注册时显示） -->
          <div v-if="!isLogin">
            <label class="block text-sm font-medium text-gray-700 mb-1">邮箱（可选）</label>
            <input
              v-model="form.email"
              type="email"
              placeholder="your@email.com"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
            />
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="text-red-500 text-sm text-center">
            {{ error }}
          </div>

          <!-- 提交按钮 -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </form>

        <!-- 切换登录/注册 -->
        <div class="mt-6 text-center">
          <p class="text-gray-600">
            {{ isLogin ? '还没有账户？' : '已有账户？' }}
            <button
              @click="toggleMode"
              class="text-primary font-semibold hover:underline"
            >
              {{ isLogin ? '立即注册' : '去登录' }}
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://111.228.46.221:8000'

const router = useRouter()
const isLogin = ref(true)
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = ''
  form.password = ''
  form.confirmPassword = ''
}

async function handleSubmit() {
  error.value = ''
  
  // 验证
  if (!isLogin.value && form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  if (form.password.length < 6) {
    error.value = '密码长度至少 6 位'
    return
  }
  
  loading.value = true
  
  try {
    if (isLogin.value) {
      // 登录
      const formData = new FormData()
      formData.append('username', form.username)
      formData.append('password', form.password)
      
      const resp = await axios.post(`${API_BASE}/api/v3/auth/login`, formData)
      
      // 保存 token
      localStorage.setItem('token', resp.data.access_token)
      localStorage.setItem('user', JSON.stringify(resp.data.user))
      
      // 跳转到首页
      router.push('/')
    } else {
      // 注册
      const resp = await axios.post(`${API_BASE}/api/v3/auth/register`, {
        username: form.username,
        password: form.password,
        email: form.email || null,
        nickname: form.username
      })
      
      // 保存 token
      localStorage.setItem('token', resp.data.access_token)
      localStorage.setItem('user', JSON.stringify({
        id: resp.data.user_id,
        username: resp.data.username
      }))
      
      // 跳转到首页
      router.push('/')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
