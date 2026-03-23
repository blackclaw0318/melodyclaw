# Chrome MCP 浏览器自动化调研文档

> 调研时间：2026-03-20  
> 目的：实现 MelodyClaw V2.0 的自动化浏览器测试

---

## 📖 什么是 MCP (Model Context Protocol)

**MCP (Model Context Protocol)** 是一种用于 AI 模型与外部工具/服务交互的标准协议。通过 MCP，AI 可以：

- 🔍 访问外部数据源
- 🛠️ 调用工具和服务
- 🌐 控制浏览器进行自动化测试
- 📊 执行复杂的工作流

---

## 🌐 Chrome MCP 浏览器自动化方案

### 方案 1: Puppeteer + MCP Server

**架构**：
```
AI Model ←→ MCP Server ←→ Puppeteer ←→ Chrome
```

**优点**：
- ✅ 完整的 Chrome 控制能力
- ✅ 支持 Headless 模式
- ✅ 成熟的生态系统
- ✅ 支持截图、PDF、网络拦截等

**缺点**：
- ❌ 需要额外的 MCP Server
- ❌ 配置相对复杂

**安装**：
```bash
npm install puppeteer
```

**示例代码**：
```javascript
// mcp-puppeteer-server.js
import puppeteer from 'puppeteer'

class BrowserMCP {
  constructor() {
    this.browser = null
    this.page = null
  }

  async launch() {
    this.browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    })
    this.page = await this.browser.newPage()
  }

  async navigate(url) {
    await this.page.goto(url, { waitUntil: 'networkidle2' })
    return await this.page.content()
  }

  async screenshot(name) {
    await this.page.screenshot({ path: `screenshots/${name}.png` })
  }

  async click(selector) {
    await this.page.click(selector)
  }

  async type(selector, text) {
    await this.page.type(selector, text)
  }

  async evaluate(script) {
    return await this.page.evaluate(script)
  }

  async close() {
    if (this.browser) {
      await this.browser.close()
    }
  }
}

export default BrowserMCP
```

---

### 方案 2: Playwright + MCP

**架构**：
```
AI Model ←→ MCP Server ←→ Playwright ←→ Chrome/Firefox/WebKit
```

**优点**：
- ✅ 支持多浏览器
- ✅ 更好的移动端模拟
- ✅ 内置等待机制
- ✅ 支持录制和回放

**缺点**：
- ❌ 包体积较大
- ❌ 学习曲线稍陡

**安装**：
```bash
npm install playwright
npx playwright install chromium
```

**示例代码**：
```javascript
// mcp-playwright-server.js
import { chromium } from 'playwright'

class PlaywrightMCP {
  constructor() {
    this.browser = null
    this.page = null
    this.context = null
  }

  async launch() {
    this.browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox']
    })
    this.context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 }
    })
    this.page = await this.context.newPage()
  }

  async navigate(url) {
    const response = await this.page.goto(url, {
      waitUntil: 'networkidle'
    })
    return {
      status: response.status(),
      content: await this.page.content()
    }
  }

  async screenshot(name) {
    await this.page.screenshot({
      path: `screenshots/${name}.png`,
      fullPage: true
    })
  }

  async click(selector) {
    await this.page.click(selector, { timeout: 5000 })
  }

  async fill(selector, value) {
    await this.page.fill(selector, value)
  }

  async waitForSelector(selector) {
    await this.page.waitForSelector(selector)
  }

  async getTextContent(selector) {
    return await this.page.textContent(selector)
  }

  async evaluate(script) {
    return await this.page.evaluate(script)
  }

  async close() {
    if (this.browser) {
      await this.browser.close()
    }
  }
}

export default PlaywrightMCP
```

---

### 方案 3: Chrome DevTools Protocol (CDP) + MCP

**架构**：
```
AI Model ←→ MCP Server ←→ CDP ←→ Chrome
```

**优点**：
- ✅ 最底层的 Chrome 控制
- ✅ 支持所有 DevTools 功能
- ✅ 性能最佳

**缺点**：
- ❌ API 复杂
- ❌ 需要直接处理 WebSocket

**安装**：
```bash
npm install chrome-remote-interface
```

**示例代码**：
```javascript
// mcp-cdp-server.js
import CDP from 'chrome-remote-interface'

class CDPMCP {
  constructor() {
    this.client = null
  }

  async connect() {
    this.client = await CDP()
    await this.client.Page.enable()
    await this.client.DOM.enable()
    await this.client.Runtime.enable()
  }

  async navigate(url) {
    await this.client.Page.navigate({ url })
    await this.client.Page.loadEventFired()
    return await this.client.DOM.getDocument()
  }

  async screenshot(name) {
    const result = await this.client.Page.captureScreenshot()
    const buffer = Buffer.from(result.data, 'base64')
    require('fs').writeFileSync(`screenshots/${name}.png`, buffer)
  }

  async evaluate(script) {
    const result = await this.client.Runtime.evaluate({
      expression: script
    })
    return result.result.value
  }

  async close() {
    if (this.client) {
      await this.client.close()
    }
  }
}

export default CDPMCP
```

---

### 方案 4: OpenClaw 内置浏览器工具

**架构**：
```
AI Model ←→ OpenClaw MCP ←→ Browser Tools
```

**优点**：
- ✅ 与 OpenClaw 深度集成
- ✅ 配置简单
- ✅ 支持会话管理

**缺点**：
- ❌ 功能可能不如专业工具全面

---

## 🎯 MelodyClaw V2.0 推荐方案

基于项目需求，我推荐使用 **方案 2: Playwright + MCP**

### 推荐理由

| 因素 | Playwright | Puppeteer | CDP |
|------|-----------|-----------|-----|
| 易用性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 功能完整性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 多浏览器支持 | ✅ | ❌ | ✅ |
| 移动端模拟 | ✅ | ⚠️ | ✅ |
| 等待机制 | 自动 | 手动 | 手动 |
| 录制回放 | ✅ | ❌ | ❌ |
| 社区支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 📦 实施步骤

### 步骤 1: 安装 Playwright

```bash
cd /root/.openclaw/workspace/melodyclaw/frontend
npm install -D playwright @playwright/test
npx playwright install chromium
```

### 步骤 2: 创建 MCP 浏览器服务

```javascript
// tests/mcp-browser.js
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'fs'
import { dirname } from 'path'

class MelodyClawBrowserMCP {
  constructor(options = {}) {
    this.browser = null
    this.page = null
    this.context = null
    this.options = {
      headless: true,
      viewport: { width: 1920, height: 1080 },
      baseURL: 'https://111.228.46.221',
      timeout: 30000,
      ...options
    }
    this.screenshotsDir = './screenshots'
    
    // 创建截图目录
    try {
      mkdirSync(this.screenshotsDir, { recursive: true })
    } catch (e) {}
  }

  /**
   * 启动浏览器
   */
  async launch() {
    console.log('🚀 启动浏览器...')
    this.browser = await chromium.launch({
      headless: this.options.headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu'
      ]
    })
    
    this.context = await this.browser.newContext({
      viewport: this.options.viewport,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    this.page = await this.context.newPage()
    console.log('✅ 浏览器启动成功')
  }

  /**
   * 访问页面
   */
  async navigate(path) {
    const url = path.startsWith('http') ? path : `${this.options.baseURL}${path}`
    console.log(`📍 访问：${url}`)
    
    const response = await this.page.goto(url, {
      waitUntil: 'networkidle',
      timeout: this.options.timeout
    })
    
    return {
      url: this.page.url(),
      status: response.status(),
      title: await this.page.title()
    }
  }

  /**
   * 截图
   */
  async screenshot(name, options = {}) {
    const filename = `${this.screenshotsDir}/${name}_${Date.now()}.png`
    console.log(`📸 截图：${filename}`)
    
    await this.page.screenshot({
      path: filename,
      fullPage: options.fullPage || false
    })
    
    return filename
  }

  /**
   * 点击元素
   */
  async click(selector) {
    console.log(`👆 点击：${selector}`)
    await this.page.click(selector, {
      timeout: 5000,
      force: options?.force || false
    })
  }

  /**
   * 填充输入框
   */
  async fill(selector, value) {
    console.log(`⌨️  输入：${selector} = "${value}"`)
    await this.page.fill(selector, value)
  }

  /**
   * 等待元素
   */
  async waitForSelector(selector, options = {}) {
    console.log(`⏳ 等待：${selector}`)
    await this.page.waitForSelector(selector, {
      state: options.state || 'visible',
      timeout: options.timeout || 5000
    })
  }

  /**
   * 获取文本内容
   */
  async getTextContent(selector) {
    return await this.page.textContent(selector)
  }

  /**
   * 获取元素数量
   */
  async count(selector) {
    return await this.page.count(selector)
  }

  /**
   * 执行 JavaScript
   */
  async evaluate(script) {
    return await this.page.evaluate(script)
  }

  /**
   * 检查元素是否存在
   */
  async isVisible(selector) {
    try {
      await this.page.waitForSelector(selector, {
        state: 'visible',
        timeout: 1000
      })
      return true
    } catch {
      return false
    }
  }

  /**
   * 获取页面所有歌曲卡片
   */
  async getSongCards() {
    return await this.page.evaluate(() => {
      const cards = document.querySelectorAll('[data-testid="song-card"]')
      return Array.from(cards).map(card => ({
        title: card.querySelector('h3')?.textContent?.trim(),
        artist: card.querySelector('p')?.textContent?.trim(),
        duration: card.querySelector('.bubble-bg')?.textContent?.trim()
      }))
    })
  }

  /**
   * 验证歌曲列表
   */
  async verifySongList(expectedCount) {
    const cards = await this.getSongCards()
    console.log(`📋 找到 ${cards.length} 首歌曲，预期 ${expectedCount} 首`)
    
    if (cards.length !== expectedCount) {
      console.log('❌ 歌曲数量不匹配')
      console.log('歌曲列表:', cards)
      return false
    }
    
    console.log('✅ 歌曲数量匹配')
    return true
  }

  /**
   * 运行完整测试流程
   */
  async runTest() {
    try {
      console.log('\n' + '='.repeat(60))
      console.log('  MelodyClaw V2.0 浏览器自动化测试')
      console.log('='.repeat(60) + '\n')
      
      // 1. 启动浏览器
      await this.launch()
      
      // 2. 访问首页
      const home = await this.navigate('/')
      console.log('首页标题:', home.title)
      console.log('首页 URL:', home.url)
      
      // 3. 截图
      await this.screenshot('home_page')
      
      // 4. 验证歌曲列表
      await this.waitForSelector('[data-testid="song-list"]')
      const songCount = await this.count('[data-testid="song-card"]')
      console.log(`歌曲卡片数量：${songCount}`)
      
      // 5. 获取歌曲详情
      const songs = await this.getSongCards()
      console.log('\n歌曲列表:')
      songs.forEach((song, i) => {
        console.log(`  ${i + 1}. ${song.title} - ${song.artist}`)
      })
      
      // 6. 验证预期歌曲
      const expectedSongs = ['小星星', '两只老虎', '生日快乐', '测试歌曲']
      const foundSongs = songs.map(s => s.title)
      
      console.log('\n验证结果:')
      expectedSongs.forEach(name => {
        const found = foundSongs.some(s => s.includes(name))
        console.log(`  ${found ? '✅' : '❌'} ${name}`)
      })
      
      // 7. 测试点击歌曲
      if (songCount > 0) {
        console.log('\n测试点击歌曲...')
        await this.click('[data-testid="song-card"]')
        await this.screenshot('record_page')
        
        // 验证进入拍摄页面
        const isRecordPage = await this.isVisible('.record-page')
        console.log('拍摄页面:', isRecordPage ? '✅' : '❌')
      }
      
      console.log('\n' + '='.repeat(60))
      console.log('  测试完成！')
      console.log('='.repeat(60) + '\n')
      
      return true
      
    } catch (error) {
      console.error('❌ 测试失败:', error)
      await this.screenshot('error')
      return false
    } finally {
      await this.close()
    }
  }

  /**
   * 关闭浏览器
   */
  async close() {
    console.log('🔒 关闭浏览器...')
    if (this.browser) {
      await this.browser.close()
    }
  }
}

// 命令行执行
if (process.argv[1].includes('mcp-browser.js')) {
  const mcp = new MelodyClawBrowserMCP({
    headless: true,
    baseURL: 'https://111.228.46.221'
  })
  
  mcp.runTest()
    .then(success => process.exit(success ? 0 : 1))
    .catch(err => {
      console.error(err)
      process.exit(1)
    })
}

export default MelodyClawBrowserMCP
```

---

### 步骤 3: 创建测试脚本

```javascript
// tests/browser-test.js
import MelodyClawBrowserMCP from './mcp-browser.js'

async function main() {
  const mcp = new MelodyClawBrowserMCP({
    headless: true,
    baseURL: 'https://111.228.46.221',
    viewport: { width: 1920, height: 1080 }
  })
  
  await mcp.runTest()
}

main()
```

---

### 步骤 4: 运行测试

```bash
cd /root/.openclaw/workspace/melodyclaw
node tests/browser-test.js
```

---

## 📊 预期输出

```
============================================================
  MelodyClaw V2.0 浏览器自动化测试
============================================================

🚀 启动浏览器...
✅ 浏览器启动成功
📍 访问：https://111.228.46.221/
首页标题：MelodyClaw
首页 URL: https://111.228.46.221/
📸 截图：./screenshots/home_page_1710936000000.png
⏳ 等待：[data-testid="song-list"]
歌曲卡片数量：5

歌曲列表:
  1. 生日快乐 - 传统
  2. 两只老虎 - 儿歌
  3. 小星星 - 儿歌
  4. 测试歌曲 - 测试
  5. 测试歌曲 - 测试

验证结果:
  ✅ 小星星
  ✅ 两只老虎
  ✅ 生日快乐
  ✅ 测试歌曲

测试点击歌曲...
📸 截图：./screenshots/record_page_1710936010000.png
拍摄页面：✅

============================================================
  测试完成！
============================================================
```

---

## 🔧 高级功能

### 1. 录制用户操作

```javascript
async recordSession() {
  const actions = []
  
  this.page.on('click', selector => {
    actions.push({ type: 'click', selector, time: Date.now() })
  })
  
  this.page.on('input', (selector, value) => {
    actions.push({ type: 'input', selector, value, time: Date.now() })
  })
  
  return actions
}
```

### 2. 性能监控

```javascript
async getPerformanceMetrics() {
  const metrics = await this.page.metrics()
  const performance = await this.page.evaluate(() => {
    return performance.getEntriesByType('navigation')[0]
  })
  
  return {
    jsHeapSize: metrics.JSHeapUsedSize,
    domContentLoaded: performance.domContentLoadedEventEnd,
    loadComplete: performance.loadEventEnd
  }
}
```

### 3. 网络拦截

```javascript
async interceptNetwork() {
  await this.page.route('**/api/**', route => {
    console.log('API 请求:', route.request().url())
    route.continue()
  })
}
```

---

## 📝 总结

| 方案 | 推荐度 | 适用场景 |
|------|--------|----------|
| **Playwright + MCP** | ⭐⭐⭐⭐⭐ | 完整 E2E 测试 |
| Puppeteer + MCP | ⭐⭐⭐⭐ | Chrome 专用测试 |
| CDP + MCP | ⭐⭐⭐ | 底层调试 |
| OpenClaw 内置 | ⭐⭐⭐⭐ | 简单任务 |

---

**下一步行动**：

1. 安装 Playwright
2. 创建 MCP 浏览器服务
3. 运行自动化测试
4. 验证歌曲列表显示

---

**最后更新**: 2026-03-20  
**负责人**: 黑 (Hei)
