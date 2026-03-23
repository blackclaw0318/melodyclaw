# 🦞 MelodyClaw V2.0

> **互动式卡拉 OK 系统** - 与小龙虾一起唱歌！

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/blackclaw0318/melodyclaw)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-development-yellow.svg)](https://github.com/blackclaw0318/melodyclaw)

---

## 📖 项目简介

MelodyClaw V2.0 是一款**互动式卡拉 OK 应用**，核心特色：

- 🎤 **实时拍摄** - 摄像头录制唱歌视频
- 🦞 **AR 互动** - 可拖动的小龙虾动画角色
- 📝 **动态歌词** - 可自由拖动的滚动歌词
- ⏱️ **智能倒计时** - 3-2-1 倒计时 + BPM 同步
- 🎬 **视频预览** - 即时回放与下载

**类似产品**: 全民 K 歌、唱吧的 Web 版本

---

## 📁 分支说明

本仓库包含以下主要分支：

| 分支 | 用途 | 内容 |
|------|------|------|
| `greyclaw_0317` | 原始设计 | 需求文档 |
| `blackclaw_0318` | 完整实现 | 全部代码 + 文档 |
| `blackclaw_0321` | 开发分支 | 最新开发进度 |
| **`blackclaw_0323`** | **文档分支** | **需求文档 + 实现方案** |

> 💡 **当前分支**: `blackclaw_0323` - 仅包含项目文档，无代码实现

---

## 📚 文档导航

### 核心文档

| 文档 | 说明 | 路径 |
|------|------|------|
| 📋 **项目需求** | 完整功能需求说明 | `docs/PROJECT_REQUIREMENTS.md` |
| 🏗️ **技术架构** | 系统架构设计 | `docs/ARCHITECTURE_V2.md` |
| 📝 **实现方案** | 详细技术实现方案 | `IMPLEMENTATION_PLAN.md` |

### 其他文档

- `docs/BACKEND.md` - 后端详细设计
- `docs/FRONTEND.md` - 前端详细设计
- `docs/TECH_STACK.md` - 技术栈说明
- `docs/DEPLOYMENT.md` - 部署指南

---

## 🎯 核心功能

### 功能模块

```
┌─────────────────────────────────────────────────────┐
│                   MelodyClaw V2.0                    │
├─────────────────────────────────────────────────────┤
│  📱 首页          │  歌曲列表、搜索、分类筛选        │
│  🎤 拍摄页        │  摄像头、小龙虾、歌词、录制      │
│  🎬 预览页        │  视频回放、保存、分享            │
│  👤 个人中心 (P2) │  作品管理、社交功能              │
└─────────────────────────────────────────────────────┘
```

### 技术特性

| 特性 | 实现方案 |
|------|----------|
| 摄像头调用 | MediaDevices API |
| 视频录制 | MediaRecorder API |
| 动画渲染 | Canvas + requestAnimationFrame |
| 拖拽交互 | Touch/Mouse 事件处理 |
| 音频播放 | Web Audio API |
| 后端框架 | FastAPI + Uvicorn |
| 前端框架 | Vue 3 + Vite + TailwindCSS |
| 数据库 | SQLite / PostgreSQL |

---

## 🚀 快速开始

### 开发环境

```bash
# 1. 克隆项目
git clone https://github.com/blackclaw0318/melodyclaw.git
cd melodyclaw

# 2. 切换到代码分支
git checkout blackclaw_0321

# 3. 安装依赖并启动
# 详见 IMPLEMENTATION_PLAN.md
```

### Docker 部署

```bash
# 使用代码分支
git checkout blackclaw_0321

# 启动服务
docker-compose -f docker-compose.v2.yml up -d

# 访问
# 前端：http://localhost:3000
# API: http://localhost:8000/docs
```

---

## 📊 项目进度

| 阶段 | 任务 | 状态 | 完成度 |
|------|------|------|--------|
| 阶段 1 | 前端基础重构 | ✅ | 100% |
| 阶段 2 | 页面开发 | ✅ | 100% |
| 阶段 3 | 后端 API 扩展 | ✅ | 100% |
| 阶段 4 | 集成测试 | ✅ | 100% |
| 阶段 5 | 优化与部署 | ⏳ | 0% |
| 阶段 6 | 商业化功能 | ⏸️ | 0% |

**总体进度**: 60%

---

## 🛠️ 技术栈

### 前端

- **框架**: Vue 3.4 + Vite
- **样式**: TailwindCSS 4
- **状态管理**: Pinia
- **路由**: Vue Router

### 后端

- **Web 框架**: FastAPI
- **服务器**: Uvicorn
- **ORM**: SQLAlchemy
- **数据库**: SQLite / PostgreSQL
- **视频处理**: FFmpeg

### 部署

- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **HTTPS**: Let's Encrypt

---

## 📝 开发计划

### 近期任务（阶段 5）

- [ ] 前端性能优化（图片懒加载、代码分割）
- [ ] 后端视频转码异步化
- [ ] Docker 部署配置更新
- [ ] 文档完善

### 后续规划（阶段 6）

- [ ] 用户系统（注册/登录）
- [ ] 社交功能（分享、评论、点赞）
- [ ] 商业化功能（VIP 音色、云存储）

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **项目仓库**: https://github.com/blackclaw0318/melodyclaw
- **作者**: blackclaw0318
- **Issue 反馈**: https://github.com/blackclaw0318/melodyclaw/issues

---

## 🙏 致谢

感谢以下开源项目：

- [Vue.js](https://vuejs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [TailwindCSS](https://tailwindcss.com/)
- [FFmpeg](https://ffmpeg.org/)

---

**最后更新**: 2026-03-23  
**当前分支**: `blackclaw_0323` (文档分支)
