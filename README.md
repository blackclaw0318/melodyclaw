# 🦞 MelodyClaw - AI 歌声克隆系统

> 完全本地化运行，CPU 推理，零 API 费用

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-green.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.4-green.svg)](https://vuejs.org)

## ✨ 特性

- 🎤 **人声分离** - Demucs AI 模型，分离人声和伴奏
- 📝 **歌词对齐** - Silero VAD，自动生成时间戳
- 🎭 **音色克隆** - 6 种预设音色，CPU 推理
- 🦞 **小龙虾动画** - 随音乐律动的可爱播放器
- 📱 **响应式设计** - 手机/平板/桌面全适配
- 🔒 **隐私安全** - 数据完全本地，不上传云端

## 🚀 快速开始

### Docker 部署 (推荐)

```bash
# 克隆项目
git clone https://github.com/blackclaw0318/melodyclaw.git
cd melodyclaw

# 启动服务
docker-compose up -d

# 访问
# 前端：http://localhost:3000
# API: http://localhost:8000/docs
```

### 本地部署

```bash
# 1. 安装依赖
pip install -r requirements-main.txt
pip install -r requirements-demucs.txt
pip install -r requirements-silero.txt
pip install -r requirements-rvc.txt

# 2. 启动服务
python services/demucs_server.py &
python services/silero_server.py &
python services/rvc_server.py &
python backend/app/main.py &

# 3. 前端
cd frontend
npm install
npm run dev
```

## 📁 项目结构

```
melodyclaw/
├── backend/          # FastAPI 后端
│   └── app/
│       ├── main.py   # 主 API
│       ├── models.py # 数据库模型
│       └── database.py
├── frontend/         # Vue3 前端
│   └── src/
│       ├── views/    # 页面组件
│       └── components/
├── services/         # AI 服务
│   ├── demucs_server.py
│   ├── silero_server.py
│   └── rvc_server.py
├── models/           # 模型文件
├── docs/             # 文档
└── docker-compose.yml
```

## 🎯 使用流程

1. **上传歌曲** - 支持 MP3/WAV/FLAC/M4A/OGG
2. **人声分离** - AI 分离人声和伴奏 (~1 倍实时)
3. **歌词对齐** - 输入歌词，自动生成时间戳
4. **音色克隆** - 选择预设音色，生成克隆版本
5. **下载结果** - 下载克隆后的音频

## 🎤 预设音色

| 音色 | 风格 | F0 范围 | 适用场景 |
|------|------|--------|----------|
| 流行男声 | 温暖明亮 | 80-400Hz | 流行、抒情 |
| 流行女声 | 清澈甜美 | 150-600Hz | 流行、抒情 |
| 摇滚男声 | 粗犷有力 | 70-350Hz | 摇滚、金属 |
| 民谣嗓音 | 朴实自然 | 90-420Hz | 民谣、乡村 |
| 童声 | 稚嫩可爱 | 200-800Hz | 儿歌、童谣 |
| 低沉嗓音 | 浑厚磁性 | 60-300Hz | 抒情、爵士 |

## 📊 性能

| 操作 | 1 分钟 | 3 分钟 | 5 分钟 |
|------|--------|--------|--------|
| 人声分离 | ~60s | ~180s | ~300s |
| 歌词对齐 | ~10s | ~30s | ~50s |
| 音色克隆 | ~90s | ~270s | ~450s |

**硬件要求:**
- CPU: 4 核+
- 内存：16GB+
- 存储：50GB+

## 📖 文档

- [部署指南](docs/DEPLOYMENT.md)
- [性能优化](docs/PERFORMANCE.md)
- [集成测试](docs/INTEGRATION_TEST.md)
- [模型测试报告](docs/MODEL_TEST_REPORT.md)

## 🛠️ 技术栈

**后端:**
- FastAPI + Uvicorn
- SQLAlchemy + SQLite
- Celery (任务队列)

**AI 模型:**
- Demucs (人声分离)
- Silero VAD (语音检测)
- Hubert + RVC (音色克隆)

**前端:**
- Vue3 + Vite
- Pinia (状态管理)
- Vue Router

**部署:**
- Docker + Docker Compose
- Nginx (反向代理)

## 📝 开发进度

- [x] 阶段 1: 环境与模型部署
- [x] 阶段 2: 后端 API 开发
- [x] 阶段 3: 前端开发
- [x] 阶段 4: 集成优化
- [ ] 阶段 5: 商业化功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

## 👥 作者

- **blackclaw0318** - [GitHub](https://github.com/blackclaw0318)

---

**Made with ❤️ by MelodyClaw Team**
