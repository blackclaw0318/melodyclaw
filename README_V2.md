# 🦞 MelodyClaw V2.0 - AI 互动式卡拉 OK 系统

> 完全本地化运行，CPU 推理，零 API 费用

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-green.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.4-green.svg)](https://vuejs.org)
[![Version](https://img.shields.io/badge/version-2.0.0-purple.svg)](https://github.com/blackclaw0318/melodyclaw)

## ✨ V2.0 新特性

- 🎤 **实时拍摄** - 摄像头调用 + 音视频录制
- 🦞 **AR 互动** - 可拖动的小龙虾动画角色
- 📝 **动态歌词** - 可拖动的滚动歌词字幕
- ⏱️ **智能倒计时** - 3-2-1 倒计时 + BPM 同步
- 🎬 **视频预览** - 即时回放 + 下载分享
- 📱 **响应式设计** - 手机/平板/桌面全适配

## 🚀 快速开始

### 方式 1：Docker 部署（推荐）

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

### 方式 2：本地部署

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

## 📖 使用流程

### V2.0 互动卡拉 OK

1. **选择歌曲** - 首页浏览歌曲列表
2. **进入拍摄** - 点击歌曲卡片
3. **调整布局** - 拖动小龙虾和歌词到舒适位置
4. **开始录制** - 点击录制按钮，3-2-1 倒计时
5. **演唱** - 跟随伴奏演唱，与小龙虾互动
6. **预览保存** - 回放视频，下载到本地

### V1.0 歌声克隆

1. **上传歌曲** - 支持 MP3/WAV/FLAC 等格式
2. **人声分离** - AI 分离人声和伴奏
3. **歌词对齐** - 自动生成时间戳
4. **音色克隆** - 选择预设音色
5. **下载结果** - 获取克隆后的音频

## 🏗️ 技术架构

### 前端技术栈

- **框架**: Vue 3.4 + Vite
- **样式**: TailwindCSS 4
- **状态管理**: Pinia
- **路由**: Vue Router
- **媒体处理**: MediaDevices API, MediaRecorder API, Web Audio API

### 后端技术栈

- **框架**: FastAPI + Uvicorn
- **数据库**: SQLite → PostgreSQL（可选）
- **AI 模型**: 
  - Demucs（人声分离）
  - Silero VAD（语音检测）
  - Hubert + RVC（音色克隆）
- **视频处理**: FFmpeg

### 部署架构

- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **服务发现**: Docker Network

## 📊 性能指标

| 操作 | 处理时间 | 内存占用 |
|------|----------|----------|
| 摄像头启动 | < 2s | 50MB |
| 视频录制 | 实时 | 200MB |
| 视频转码 | 0.5x 实时 | 500MB |
| 动画帧率 | 60fps | 100MB |

**硬件要求**:
- CPU: 4 核+
- 内存：16GB+
- 存储：50GB+
- 摄像头：720p/1080p

## 📁 项目结构

```
melodyclaw/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # 主 API
│   │   ├── models.py     # V1 数据模型
│   │   ├── models_v2.py  # V2 数据模型
│   │   └── routes_v2.py  # V2 API 路由
│   └── services/
│       └── video_processor.py  # 视频处理
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
    ├── REQUIREMENTS_V2.md
    ├── ARCHITECTURE_V2.md
    └── DEPLOYMENT.md
```

## 🧪 测试

### 运行自动化测试

```bash
# 前端测试
cd frontend
npm run dev

# 后端测试
cd backend/app
python main.py

# 运行测试
source venv/bin/activate
python tests/test_v2_frontend.py
python tests/test_v2_backend.py
python tests/test_v2_e2e.py
```

### 测试结果

| 测试类型 | 通过 | 总计 | 通过率 |
|----------|------|------|--------|
| 前端测试 | 5 | 5 | 100% |
| 后端测试 | 6 | 6 | 100% |
| 端到端测试 | 4 | 4 | 100% |
| **总计** | **15** | **15** | **100%** |

## 📝 API 文档

### V2 核心端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v2/recordings` | POST | 上传作品 |
| `/api/v2/recordings` | GET | 作品列表 |
| `/api/v2/recordings/{id}` | GET | 作品详情 |
| `/api/v2/recordings/{id}/video` | GET | 下载视频 |
| `/api/v2/recordings/{id}` | DELETE | 删除作品 |
| `/api/v2/recordings/{id}/like` | POST | 点赞作品 |

完整 API 文档：http://localhost:8000/docs

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/blackclaw0318/melodyclaw.git
cd melodyclaw

# 后端
python -m venv venv
source venv/bin/activate
pip install -r requirements-main.txt

# 前端
cd frontend
npm install

# 运行开发服务器
# 后端：python backend/app/main.py
# 前端：npm run dev
```

## 📄 许可证

MIT License

## 👥 作者

- **blackclaw0318** - [GitHub](https://github.com/blackclaw0318)

## 🔗 相关链接

- [V1.0 文档](docs/BACKEND.md)
- [V2.0 需求文档](docs/REQUIREMENTS_V2.md)
- [V2.0 架构设计](docs/ARCHITECTURE_V2.md)
- [部署指南](docs/DEPLOYMENT.md)

---

**Made with ❤️ by MelodyClaw Team**
