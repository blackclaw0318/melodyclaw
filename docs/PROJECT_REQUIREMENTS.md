# MelodyClaw 项目完整需求与说明文档

> **版本**: 2.0  
> **最后更新**: 2026-03-21  
> **作者**: blackclaw0318  
> **状态**: 正式发布

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [产品定位与目标](#2-产品定位与目标)
3. [功能需求](#3-功能需求)
4. [技术架构](#4-技术架构)
5. [开发计划与进度](#5-开发计划与进度)
6. [部署指南](#6-部署指南)
7. [API 文档](#7-api 文档)
8. [测试策略](#8-测试策略)
9. [性能指标](#9-性能指标)
10. [待办事项](#10-待办事项)

---

## 1. 项目概述

### 1.1 项目名称

**MelodyClaw** - AI 互动式卡拉 OK 系统

### 1.2 版本历史

| 版本 | 日期 | 类型 | 说明 |
|------|------|------|------|
| V1.0 | 2026-03-18 | 歌声克隆 | AI 歌声克隆系统 |
| V2.0 | 2026-03-20 | 互动卡拉 OK | 实时拍摄 + AR 互动 |

### 1.3 核心特性

- 🎤 **实时拍摄** - 摄像头调用 + 音视频录制
- 🦞 **AR 互动** - 可拖动的小龙虾动画角色
- 📝 **动态歌词** - 可拖动的滚动歌词字幕
- ⏱️ **智能倒计时** - 3-2-1 倒计时 + BPM 同步
- 🎬 **视频预览** - 即时回放 + 下载分享
- 📱 **响应式设计** - 手机/平板/桌面全适配
- 🔒 **隐私安全** - 数据完全本地，不上传云端

### 1.4 项目仓库

- **Fork 仓库**: https://github.com/blackclaw0318/melodyclaw
- **原仓库**: https://github.com/GreyClaw0311/melodyclaw
- **工作分支**: `blackclaw_0321`
- **源分支**: `greyclaw_0317`

---

## 2. 产品定位与目标

### 2.1 产品定位

MelodyClaw V2.0 是一款**互动式卡拉 OK 应用**（类似"全民 K 歌"的 Web 版本），核心创新点：

- 用户可录制自己唱歌的视频
- 虚拟小龙虾可与视频中的人物互动
- 可自由拖动位置的滚动歌词
- 3-2-1 倒计时后自动播放伴奏

### 2.2 目标用户

- 喜欢唱歌的普通用户
- 想要录制唱歌短视频的用户
- 喜欢创意互动体验的年轻人

### 2.3 核心使用场景

```
用户打开 App → 选择想唱的歌曲 → 进入拍摄页面
→ 调整小龙虾和歌词位置 → 3-2-1 倒计时 → 开始演唱
→ 演唱过程中与小龙虾互动 → 录制完成 → 预览/保存/分享
```

---

## 3. 功能需求

### 3.1 功能模块总览

| 模块 | 功能 | 优先级 | 复杂度 | 状态 |
|------|------|--------|--------|------|
| 首页歌曲列表 | 展示可合唱歌曲 | P0 | 低 | ✅ 完成 |
| 拍摄页面 | 摄像头调用、预览 | P0 | 高 | ✅ 完成 |
| 歌词字幕 | 滚动歌词、位置拖动 | P0 | 中 | ✅ 完成 |
| 小龙虾动画 | AR 互动、位置拖动 | P0 | 高 | ✅ 完成 |
| 录制功能 | 倒计时、音视频录制 | P0 | 高 | ✅ 完成 |
| 视频预览 | 回放、保存、分享 | P1 | 中 | ✅ 完成 |
| 歌曲上传 | 用户上传新歌 | P1 | 低 | ⏳ 待完成 |
| 用户系统 | 登录、作品管理 | P2 | 中 | ⏸️ 规划中 |

### 3.2 详细功能描述

#### 3.2.1 首页 - 歌曲列表

**页面样式**: 全民 K 歌首页卡片式布局

**功能点**:
- 网格展示歌曲封面卡片（2 列或 3 列）
- 每首歌曲显示：封面图、歌名、歌手、时长、已合唱次数
- 搜索框：支持歌名/歌手搜索
- 分类筛选：流行、摇滚、民谣等
- 上传按钮：用户上传新歌（P1）

**数据结构**:
```json
{
  "songs": [
    {
      "id": 1,
      "title": "测试歌曲",
      "artist": "原唱歌手",
      "duration": 245,
      "cover_url": "/covers/song_1.jpg",
      "accompaniment_url": "/audio/song_1 伴奏.wav",
      "lyrics": "[00:05.00] 第一句歌词...",
      "duet_count": 128,
      "bpm": 120
    }
  ]
}
```

#### 3.2.2 拍摄页面 - 核心功能

**页面布局**（竖屏模式）:

```
┌─────────────────────────────────┐
│  ←返回     拍摄中     [切换镜头] │
├─────────────────────────────────┤
│                                 │
│         ┌─────────────┐         │
│         │             │         │
│         │  摄像头画面  │         │
│         │  (全屏预览)  │         │
│         │             │         │
│         │    🦞        │         │
│         │  (小龙虾)    │         │
│         │             │         │
│         └─────────────┘         │
│                                 │
├─────────────────────────────────┤
│  [歌词] [动画]    [🎤录制]    │
│  按钮   按钮       大按钮       │
└─────────────────────────────────┘
```

**功能点**:

1. **摄像头调用**
   - 默认调用后置摄像头
   - 支持前后摄像头切换
   - 分辨率：720p/1080p 可选
   - 帧率：30fps

2. **歌词字幕模块**
   - 点击"歌词"按钮展开/收起歌词面板
   - 歌词自动滚动（跟随伴奏时间）
   - 当前歌词高亮放大
   - **支持拖动**: 用户可长按歌词区域拖动到任意位置
   - 录制开始后位置锁定

3. **小龙虾动画模块**
   - 点击"动画"按钮显示/隐藏小龙虾
   - 小龙虾随音乐节奏摆动（钳子开合、身体晃动）
   - **支持拖动**: 用户可长按小龙虾拖动到任意位置
   - 录制开始后位置锁定
   - 可选：小龙虾吐出气泡音符特效

4. **录制功能**
   - 点击录制按钮 → 弹出倒计时设置（默认 3 秒）
   - 3-2-1 倒计时动画（屏幕中央大数字）
   - 倒计时结束 → 自动播放伴奏
   - 开始录制：同时录制摄像头视频 + 麦克风音频 + 伴奏混音
   - 录制中显示：录制时长、暂停按钮、结束按钮
   - 录制时长限制：最长 5 分钟（可配置）

#### 3.2.3 录制倒计时设置

**倒计时配置弹窗**:

```
┌─────────────────────────────┐
│  倒计时设置              [×] │
├─────────────────────────────┤
│                             │
│  倒计时时长：[3] 秒          │
│  ▬▬▬▬●▬▬▬▬▬▬               │
│  1    3    5    10          │
│                             │
│  ☑ 倒计时数字跟随 BPM 节奏   │
│                             │
│  节奏预览：[▶ 播放]         │
│                             │
│         [取消] [确定]       │
└─────────────────────────────┘
```

**BPM 同步逻辑**:
- 读取歌曲 BPM 信息
- 计算每拍时长：`beat_duration = 60 / BPM`
- 倒计时数字切换时机与节拍对齐
- 示例：BPM=120 → 每拍 0.5 秒 → "3"持续 2 拍、"2"持续 2 拍、"1"持续 2 拍

#### 3.2.4 视频预览与保存

**预览页面**:

```
┌─────────────────────────────────┐
│  ←返回        预览              │
├─────────────────────────────────┤
│                                 │
│         ┌─────────────┐         │
│         │             │         │
│         │  视频播放   │         │
│         │  (含小龙虾)  │         │
│         │             │         │
│         └─────────────┘         │
│                                 │
│  [◀] ━━━━━━━●━━━━━━━ [▶]      │
│  00:00 / 03:45                  │
│                                 │
├─────────────────────────────────┤
│  [🔄 重录]  [💾 保存]  [📤 分享] │
└─────────────────────────────────┘
```

**功能点**:
- 视频播放（含小龙虾动画和歌词字幕）
- 进度条拖动
- 重录：返回拍摄页面重新录制
- 保存：下载视频到本地（MP4 格式）
- 分享：生成分享链接（P2 功能）

### 3.3 后端 API 需求

#### 3.3.1 新增 API 端点

| 端点 | 方法 | 描述 | 状态 |
|------|------|------|------|
| `/api/v2/songs` | GET | 获取歌曲列表（含封面、BPM 等） | ✅ 完成 |
| `/api/v2/songs/{id}/accompaniment` | GET | 获取伴奏音频 | ✅ 完成 |
| `/api/v2/songs/{id}/lyrics` | GET | 获取歌词（含时间戳） | ✅ 完成 |
| `/api/v2/recordings` | POST | 上传录制作品 | ✅ 完成 |
| `/api/v2/recordings/{id}` | GET | 获取作品详情 | ✅ 完成 |
| `/api/v2/recordings/{id}/video` | GET | 下载作品视频 | ✅ 完成 |
| `/api/v2/recordings/{id}` | DELETE | 删除作品 | ✅ 完成 |
| `/api/v2/recordings/{id}/like` | POST | 点赞作品 | ✅ 完成 |
| `/api/v2/recordings/{id}/view` | POST | 播放统计 | ✅ 完成 |

#### 3.3.2 数据库模型变更

**新增表：recordings_v2（录制作品）**

```sql
CREATE TABLE recordings_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid VARCHAR(64) UNIQUE NOT NULL,
    song_id INTEGER NOT NULL,
    user_id INTEGER,  -- P2: 用户系统
    video_file VARCHAR(512),
    thumbnail_file VARCHAR(512),
    duration FLOAT,
    lobster_position JSON,  -- 小龙虾位置 {x, y}
    lyrics_position JSON,   -- 歌词位置 {x, y}
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs(id)
);
```

**修改表：songs（歌曲）**

```sql
ALTER TABLE songs ADD COLUMN cover_file VARCHAR(512);
ALTER TABLE songs ADD COLUMN bpm INTEGER;
ALTER TABLE songs ADD COLUMN accompaniment_file VARCHAR(512);
ALTER TABLE songs ADD COLUMN duet_count INTEGER DEFAULT 0;
```

---

## 4. 技术架构

### 4.1 系统架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   iOS Safari │ │ Android Chrome│ │ Desktop Chrome│          │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Vue3)                             │
│  - 页面层：Home, Record, Preview, Profile                       │
│  - 组件层：Camera, Lobster, Lyrics, Recorder                    │
│  - 服务层：Camera Service, Audio Service, Video Service         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端层 (FastAPI)                          │
│  - API Routes: /api/v2/songs, /api/v2/recordings               │
│  - Business Logic: Song Service, Recording Service             │
│  - Data Access: SQLite Database, File Storage                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        基础设施层                                │
│  - FFmpeg (视频转码)  - Nginx (CDN)  - Cloud Storage           │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 前端技术栈

| 技术 | 方案 | 说明 |
|------|------|------|
| 框架 | Vue 3.4 + Vite | 现代化前端框架 |
| 样式 | TailwindCSS 4 | 原子化 CSS |
| 状态管理 | Pinia | Vue 官方状态管理 |
| 路由 | Vue Router | 单页应用路由 |
| 摄像头 | MediaDevices API | 浏览器原生摄像头访问 |
| 视频录制 | MediaRecorder API | 浏览器原生录制 |
| 动画 | Canvas + requestAnimationFrame | 高性能动画渲染 |
| 音频播放 | Web Audio API | 精确控制、低延迟 |

### 4.3 后端技术栈

| 技术 | 方案 | 说明 |
|------|------|------|
| Web 框架 | FastAPI + Uvicorn | 高性能异步框架 |
| 数据库 | SQLite → PostgreSQL | 根据规模选择 |
| ORM | SQLAlchemy | Python ORM |
| 视频处理 | FFmpeg | 视频编码、合并 |
| 文件存储 | 本地 + 云存储 (可选) | 视频文件管理 |

### 4.4 项目结构

```
melodyclaw/
├── backend/              # FastAPI 后端
│   └── app/
│       ├── main.py       # 主 API
│       ├── models.py     # V1 数据模型
│       ├── models_v2.py  # V2 数据模型
│       └── routes_v2.py  # V2 API 路由
├── frontend/             # Vue3 前端
│   └── src/
│       ├── components/   # 可复用组件
│       │   ├── camera/   # 摄像头组件
│       │   ├── lobster/  # 小龙虾动画
│       │   ├── lyrics/   # 歌词组件
│       │   └── recorder/ # 录制组件
│       ├── composables/  # 组合式函数
│       │   ├── useCamera.js
│       │   ├── useDraggable.js
│       │   ├── useRecorder.js
│       │   └── useBPM.js
│       └── views/        # 页面组件
│           ├── Home.vue      # 首页
│           ├── Record.vue    # 拍摄页
│           └── Preview.vue   # 预览页
├── services/             # AI 服务
│   ├── demucs_server.py
│   ├── silero_server.py
│   └── rvc_server.py
├── tests/                # 自动化测试
│   ├── test_v2_frontend.py
│   ├── test_v2_backend.py
│   └── test_v2_e2e.py
├── docker-compose.v2.yml # Docker 配置
└── docs/                 # 文档
```

### 4.5 音视频处理流程

```
┌─────────────────────────────────────────────────────────┐
│                    录制流程                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  摄像头 ──→ MediaStream ──┐                            │
│                           ├──→ MediaRecorder ──→ WebM  │
│  麦克风 ──→ MediaStream ──┤                            │
│                           │                            │
│  伴奏 ──→ Web Audio ──────┘                            │
│                                                         │
│  录制完成 ──→ 上传后端 ──→ FFmpeg 转码 ──→ MP4         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 5. 开发计划与进度

### 5.1 整体进度

| 阶段 | 任务 | 状态 | 完成度 |
|------|------|------|--------|
| 阶段 1 | 前端基础重构 | ✅ 完成 | 100% |
| 阶段 2 | 页面开发 | ✅ 完成 | 100% |
| 阶段 3 | 后端 API 扩展 | ✅ 完成 | 100% |
| 阶段 4 | 集成测试 | ✅ 完成 | 100% |
| 阶段 5 | 优化与部署 | ⏳ 进行中 | 0% |
| 阶段 6 | 商业化功能 | ⏸️ 待开始 | 0% |

**总体完成度：60%**

### 5.2 已完成工作

#### 阶段 1：前端基础重构（100%）

- [x] TailwindCSS 配置
- [x] composables 核心 Hook
  - [x] useCamera.js（摄像头控制）
  - [x] useDraggable.js（拖拽功能）
  - [x] useBPM.js（BPM 节奏计算）
  - [x] useRecorder.js（录制功能）
- [x] 核心组件
  - [x] CameraView.vue
  - [x] LobsterAnimation.vue
  - [x] LyricsScroll.vue
  - [x] Countdown.vue
  - [x] Recorder.vue
- [x] API 客户端封装

**测试结果：5/5 通过 ✅**

#### 阶段 2：页面开发（100%）

- [x] Home.vue（歌曲列表卡片布局）
- [x] Record.vue（拍摄页面）
- [x] Preview.vue（预览页面）
- [x] SongCard.vue（歌曲卡片组件）
- [x] 路由配置更新

**测试结果：4/4 通过 ✅**

#### 阶段 3：后端 API 扩展（100%）

- [x] models_v2.py（RecordingV2 模型）
- [x] routes_v2.py（V2 API 端点）
- [x] migrate_v2.py（数据库迁移脚本）
- [x] 数据库表扩展

**测试结果：6/6 通过 ✅**

#### 阶段 4：集成测试（100%）

- [x] test_v2_frontend.py（前端自动化测试）
- [x] test_v2_backend.py（后端集成测试）
- [x] test_v2_e2e.py（端到端联调测试）

**测试结果：15/15 通过 ✅**

### 5.3 待完成任务

#### 阶段 5：优化与部署（0%）

**任务 5.1：性能优化（预计 1 天）**

- [ ] 前端性能优化
  - [ ] 图片懒加载（Intersection Observer）
  - [ ] 视频分片上传
  - [ ] 动画性能优化（Canvas 渲染）
  - [ ] 代码分割（Vue Router 懒加载）
  - [ ] Service Worker 缓存

- [ ] 后端性能优化
  - [ ] 视频转码异步化（Celery 任务队列）
  - [ ] 文件 CDN 集成
  - [ ] 数据库索引优化
  - [ ] 响应缓存（Redis）

- [ ] 内存优化
  - [ ] 模型分步加载策略
  - [ ] 16GB 内存压力测试
  - [ ] 模型加载/释放逻辑优化

**任务 5.2：Docker 部署更新（预计 1 天）**

- [ ] Dockerfile 更新
- [ ] docker-compose.yml 更新
- [ ] Nginx 配置更新

**任务 5.3：文档更新（预计 0.5 天）**

- [ ] README.md 更新（V2.0 功能说明）
- [ ] DEPLOYMENT.md 更新（部署指南）
- [ ] API 文档更新（Swagger/OpenAPI）
- [ ] 用户手册（使用流程）

#### 阶段 6：商业化功能（0%）

- [ ] 用户系统（注册/登录、个人中心、作品管理）
- [ ] 社交功能（分享、评论、点赞/打赏、排行榜）
- [ ] 付费功能（VIP 音色库、高级音效、云存储）

### 5.4 里程碑

| 里程碑 | 目标日期 | 状态 |
|--------|----------|------|
| V2.0 核心功能 | 2026-03-20 | ✅ 完成 |
| V2.0 性能优化 | 2026-03-22 | ⏳ 进行中 |
| V2.0 正式发布 | 2026-03-25 | ⏸️ 待完成 |
| V3.0 商业化 | 2026-04-01 | ⏸️ 待完成 |

---

## 6. 部署指南

### 6.1 Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/blackclaw0318/melodyclaw.git
cd melodyclaw

# 启动所有服务
docker-compose -f docker-compose.v2.yml up -d

# 访问
# 前端：http://localhost:3000
# API: http://localhost:8000/docs
```

### 6.2 本地部署

```bash
# 1. 后端服务
cd melodyclaw
source venv/bin/activate
pip install -r requirements-main.txt
python backend/app/main.py

# 2. 前端服务
cd frontend
npm install
npm run dev

# 访问
# 前端：http://localhost:3001
# API: http://localhost:8000
```

### 6.3 多虚拟环境方案

```
melodyclaw/
├── venv/                    # 主应用 (FastAPI + 轻量依赖)
├── venv-demucs/             # Demucs 人声分离服务
├── venv-silero/             # Silero VAD 歌词对齐服务
├── venv-rvc/                # RVC 音色克隆服务
└── services/
    ├── demucs_server.py     # Demucs HTTP 服务
    ├── silero_server.py     # Silero HTTP 服务
    └── rvc_server.py        # RVC HTTP 服务
```

**启动服务**:

```bash
# 1. 启动 Demucs 服务 (端口 8001)
source venv-demucs/bin/activate
python services/demucs_server.py &

# 2. 启动 Silero 服务 (端口 8002)
source venv-silero/bin/activate
python services/silero_server.py &

# 3. 启动 RVC 服务 (端口 8003)
source venv-rvc/bin/activate
python services/rvc_server.py &

# 4. 启动主 API (端口 8000)
source venv/bin/activate
python backend/app/main.py &
```

### 6.4 生产部署

**Nginx 反向代理**:

```nginx
server {
    listen 80;
    server_name melodyclaw.example.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
        client_max_body_size 500M;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /videos {
        alias /data/videos;
        add_header Cache-Control "public, max-age=31536000";
    }
}
```

**HTTPS 配置**:

```bash
# 使用 Let's Encrypt
certbot --nginx -d melodyclaw.example.com
```

---

## 7. API 文档

### 7.1 V2 核心端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v2/songs` | GET | 获取歌曲列表 |
| `/api/v2/songs/{id}` | GET | 获取歌曲详情 |
| `/api/v2/songs/{id}/accompaniment` | GET | 获取伴奏音频 |
| `/api/v2/songs/{id}/lyrics` | GET | 获取歌词 |
| `/api/v2/recordings` | POST | 上传作品 |
| `/api/v2/recordings` | GET | 作品列表 |
| `/api/v2/recordings/{id}` | GET | 作品详情 |
| `/api/v2/recordings/{id}/video` | GET | 下载视频 |
| `/api/v2/recordings/{id}` | DELETE | 删除作品 |
| `/api/v2/recordings/{id}/like` | POST | 点赞作品 |
| `/api/v2/recordings/{id}/view` | POST | 播放统计 |

完整 API 文档：http://localhost:8000/docs

### 7.2 数据模型

**SongV2**:
```python
{
    "id": int,
    "title": str,
    "artist": str,
    "cover_file": str,
    "bpm": int,
    "duration": float,
    "original_file": str,
    "accompaniment_file": str,
    "lyrics": str,
    "category": str,
    "duet_count": int
}
```

**RecordingV2**:
```python
{
    "id": int,
    "uuid": str,
    "song_id": int,
    "user_id": int,
    "video_file": str,
    "thumbnail_file": str,
    "duration": float,
    "lobster_position": {"x": int, "y": int},
    "lyrics_position": {"x": int, "y": int},
    "view_count": int,
    "like_count": int,
    "share_count": int,
    "created_at": datetime
}
```

---

## 8. 测试策略

### 8.1 测试类型

| 测试类型 | 工具 | 覆盖范围 |
|----------|------|----------|
| 单元测试 | Vitest + Pytest | 组件、函数 |
| 集成测试 | Pytest | API 端点 |
| E2E 测试 | Playwright | 完整用户流程 |

### 8.2 测试结果

| 测试类型 | 通过 | 总计 | 通过率 |
|----------|------|------|--------|
| 前端测试 | 5 | 5 | 100% |
| 后端测试 | 6 | 6 | 100% |
| 端到端测试 | 4 | 4 | 100% |
| **总计** | **15** | **15** | **100%** |

### 8.3 运行测试

```bash
# 前端测试
cd frontend
npm run test

# 后端测试
source venv/bin/activate
python -m pytest tests/

# E2E 测试
python tests/test_v2_e2e.py
```

---

## 9. 性能指标

### 9.1 前端性能

| 操作 | 目标值 | 当前值 |
|------|--------|--------|
| 页面加载时间 | < 3 秒 | - |
| 摄像头启动时间 | < 2 秒 | - |
| 动画帧率 | ≥ 50 fps | - |
| 录制延迟 | < 100ms | - |
| 视频保存时间 | < 10 秒（1 分钟视频） | - |

### 9.2 后端性能

| 操作 | 处理时间 | 内存占用 |
|------|----------|----------|
| 视频转码 | 0.5x 实时 | 500MB |
| API 响应 | < 200ms | 200MB |
| 文件上传 | 实时 | 100MB |

### 9.3 硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8 核 |
| 内存 | 8GB | 16GB |
| 存储 | 30GB | 50GB |
| 摄像头 | 720p | 1080p |

---

## 10. 待办事项

### 10.1 立即执行（阶段 5）

1. **性能优化**（优先级：高）
   - 视频上传码率控制
   - 动画帧率优化（目标 60fps）
   - 内存泄漏检查

2. **Docker 部署**（优先级：高）
   - 更新 docker-compose.yml
   - 测试容器化部署

3. **文档完善**（优先级：中）
   - README.md 更新
   - API 文档生成

### 10.2 后续规划（阶段 6）

- 用户系统设计
- 社交功能开发
- 商业化变现

### 10.3 技术难点与解决方案

| 难点 | 解决方案 | 状态 |
|------|----------|------|
| 音视频同步 | Web Audio API 统一时钟源 | ✅ 已解决 |
| 小龙虾动画性能 | Canvas + requestAnimationFrame | ✅ 已解决 |
| 拖拽后位置锁定 | 状态管理 + 坐标记录 | ✅ 已解决 |
| 视频文件过大 | FFmpeg 转码压缩 + 云存储 | ⏳ 待实施 |

---

## 附录

### A. 参考产品

- 全民 K 歌
- 唱吧
- TikTok 音乐拍摄
- Instagram Reels

### B. 技术文档链接

- [MediaDevices API](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices)
- [MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/Web_Audio_API)
- [Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)

### C. 相关链接

- GitHub: https://github.com/blackclaw0318/melodyclaw
- API 文档：http://localhost:8000/docs
- 前端：http://localhost:3000

---

**文档状态**: 正式发布  
**最后更新**: 2026-03-21  
**维护者**: blackclaw0318
