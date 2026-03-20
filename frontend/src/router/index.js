import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Songs from '../views/Songs.vue'
import Record from '../views/Record.vue'
import Preview from '../views/Preview.vue'
import Clone from '../views/Clone.vue'
import Auth from '../views/Auth.vue'
import Profile from '../views/Profile.vue'

const routes = [
  { 
    path: '/', 
    name: 'Home', 
    component: Home,
    meta: { title: 'MelodyClaw - 首页' }
  },
  { 
    path: '/auth', 
    name: 'Auth', 
    component: Auth,
    meta: { title: '登录/注册 - MelodyClaw' }
  },
  { 
    path: '/profile', 
    name: 'Profile', 
    component: Profile,
    meta: { title: '个人中心 - MelodyClaw' }
  },
  { 
    path: '/songs', 
    name: 'Songs', 
    component: Songs,
    meta: { title: '歌曲管理 - MelodyClaw' }
  },
  { 
    path: '/record/:songId', 
    name: 'Record', 
    component: Record,
    meta: { title: '拍摄 - MelodyClaw' }
  },
  { 
    path: '/preview/:id', 
    name: 'Preview', 
    component: Preview,
    meta: { title: '预览 - MelodyClaw' },
    props: true
  },
  { 
    path: '/clone', 
    name: 'Clone', 
    component: Clone,
    meta: { title: '克隆 - MelodyClaw' }
  }
]

const router = createRouter({ 
  history: createWebHistory(), 
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫：更新页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'MelodyClaw'
  next()
})

export default router
