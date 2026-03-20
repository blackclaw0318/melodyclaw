<template>
  <div class="profile-page min-h-screen bg-gray-50">
    <!-- 头部背景 -->
    <div class="profile-header bg-gradient-to-r from-primary to-secondary h-48 relative">
      <div class="absolute -bottom-16 left-1/2 -translate-x-1/2">
        <div class="w-32 h-32 rounded-full bg-white p-1 shadow-xl">
          <div class="w-full h-full rounded-full bg-gray-200 flex items-center justify-center text-4xl">
            {{ user?.avatar_url ? `<img :src="user.avatar_url" class="w-full h-full rounded-full object-cover"/>` : '👤' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 用户信息 -->
    <div class="profile-info pt-20 pb-6 text-center">
      <h1 class="text-2xl font-bold text-gray-800">{{ user?.nickname || user?.username }}</h1>
      <p class="text-gray-500 mt-1">@{{ user?.username }}</p>
      
      <!-- VIP 标识 -->
      <div v-if="user?.is_vip" class="inline-block mt-2 px-3 py-1 bg-yellow-400 text-yellow-900 text-sm font-semibold rounded-full">
        👑 VIP 会员
      </div>
      
      <!-- 统计 -->
      <div class="flex justify-center gap-8 mt-6">
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-800">{{ stats.works || 0 }}</div>
          <div class="text-sm text-gray-500">作品</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-800">{{ stats.followers || 0 }}</div>
          <div class="text-sm text-gray-500">粉丝</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-800">{{ stats.likes || 0 }}</div>
          <div class="text-sm text-gray-500">获赞</div>
        </div>
      </div>
    </div>

    <!-- 选项卡 -->
    <div class="profile-tabs border-b bg-white">
      <div class="max-w-4xl mx-auto flex">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentTab = tab.id"
          class="flex-1 py-4 text-center font-medium transition-colors"
          :class="currentTab === tab.id ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'"
        >
          {{ tab.name }}
        </button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="profile-content max-w-4xl mx-auto p-4">
      <!-- 我的作品 -->
      <div v-if="currentTab === 'works'" class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i" class="aspect-square bg-gray-200 rounded-lg flex items-center justify-center text-gray-400">
          作品 {{ i }}
        </div>
      </div>
      
      <!-- 收藏 -->
      <div v-if="currentTab === 'favorites'" class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div v-for="i in 3" :key="i" class="aspect-square bg-gray-200 rounded-lg flex items-center justify-center text-gray-400">
          收藏 {{ i }}
        </div>
      </div>
      
      <!-- 设置 -->
      <div v-if="currentTab === 'settings'" class="space-y-4">
        <div class="bg-white rounded-lg p-4 shadow">
          <h3 class="font-semibold mb-4">账户设置</h3>
          <button @click="logout" class="w-full py-2 text-red-500 hover:bg-red-50 rounded transition-colors">
            退出登录
          </button>
        </div>
        
        <div class="bg-white rounded-lg p-4 shadow">
          <h3 class="font-semibold mb-4">VIP 会员</h3>
          <div v-if="user?.is_vip" class="text-green-600">
            ✓ 已是 VIP 会员
          </div>
          <button v-else class="w-full py-2 bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900 font-semibold rounded hover:opacity-90">
            👑 开通 VIP
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const user = ref(null)
const currentTab = ref('works')
const stats = reactive({
  works: 0,
  followers: 0,
  likes: 0
})

const tabs = [
  { id: 'works', name: '作品' },
  { id: 'favorites', name: '收藏' },
  { id: 'settings', name: '设置' }
]

onMounted(() => {
  // 从 localStorage 加载用户信息
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  } else {
    router.push('/auth')
  }
})

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/')
}
</script>

<style scoped>
.profile-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
