# MelodyClaw

歌声克隆系统 - 完全本地化运行，CPU 推理

## 项目概述

MelodyClaw 是一个歌声克隆系统，核心功能：
- **人声分离** (Demucs) - 从歌曲中分离人声和伴奏
- **歌词对齐** (Silero VAD) - 语音活动检测，对齐歌词时间戳
- **音色克隆** (RVC v2) - 基于检索的语音转换

## 系统要求

- **主机:** 4c16g Ubuntu Server (4 核 16GB，无 GPU)
- **Python:** 3.10+
- **存储:** 10GB+ 可用空间

## 快速开始

### 环境搭建

```bash
# 1. 运行环境设置脚本
chmod +x setup_env.sh
./setup_env.sh

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 运行测试
./run_phase1_tests.sh
```

## 项目结构

```
melodyclaw/
├── tests/              # 测试脚本
│   ├── test_demucs.py      # Demucs 人声分离测试
│   ├── test_silero_vad.py  # Silero VAD 测试
│   ├── test_rvc.py         # RVC v2 测试
│   └── test_memory.py      # 内存压力测试
├── docs/               # 文档
│   └── PHASE1_SETUP.md # 环境设置指南
├── requirements.txt    # Python 依赖
├── requirements-rvc.txt # RVC 专用依赖
├── setup_env.sh        # 环境设置脚本
├── run_phase1_tests.sh # 测试运行脚本
└── README.md           # 本文件
```

## 开发阶段

### 阶段 1：环境搭建与模型部署测试 ✅ (进行中)

- [x] Python 虚拟环境配置
- [x] 基础依赖安装 (FastAPI, numpy, scipy, demucs, silero-vad)
- [x] Demucs 模型测试脚本
- [x] Silero VAD 测试脚本
- [x] RVC v2 测试脚本
- [x] 内存压力测试脚本
- [ ] 模型下载与验证
- [ ] CPU 推理性能基准测试

### 阶段 2：后端 API 开发 (待开始)

- [ ] FastAPI 项目搭建
- [ ] 歌曲上传/管理 API
- [ ] 人声分离 API
- [ ] 歌词对齐 API
- [ ] 音色克隆 API
- [ ] Celery 任务队列

### 阶段 3：前端开发 (待开始)

- [ ] Vue3 项目搭建
- [ ] 首页（小龙虾动画播放器）
- [ ] 歌曲管理页面
- [ ] 歌词编辑页面
- [ ] 克隆任务管理

### 阶段 4：集成测试与优化 (待开始)

- [ ] 端到端测试
- [ ] 性能优化
- [ ] Docker 部署

## 技术栈

- **后端:** FastAPI + Celery + Redis
- **前端:** Vue3 + Vite + Pinia
- **AI 模型:** Demucs + RVC v2 + Silero VAD
- **数据库:** SQLite (轻量级)
- **部署:** Docker + Nginx

## 内存优化策略

针对 16GB 内存限制，采用**顺序模型加载**策略：

1. 一次只加载一个模型到内存
2. 处理完成后立即卸载
3. 使用 `gc.collect()` 强制垃圾回收
4. 避免同时加载多个大模型

详见：`docs/PHASE1_SETUP.md`

## GitHub

- **Fork:** blackclaw0318/melodyclaw
- **分支:** blackclaw_0318
- **源仓库:** GreyClaw0311/melodyclaw

## License

MIT

---

_HandFoot 商业帝国 · AI 算法工程部_
