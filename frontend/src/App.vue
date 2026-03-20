<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">🦞 MelodyClaw</div>
      <div class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/songs">歌曲</router-link>
      </div>
    </nav>
    <main class="main-content"><router-view /></main>
  </div>
</template>

<script setup></script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}
.nav-brand { font-size: 1.5rem; font-weight: bold; }
.nav-links a { color: white; text-decoration: none; margin-left: 2rem; }
.main-content { padding: 2rem; max-width: 1200px; margin: 0 auto; }
</style>
