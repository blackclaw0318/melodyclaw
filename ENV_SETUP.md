# MelodyClaw 多虚拟环境方案

## 环境结构

```
melodyclaw/
├── venv/                    # 主应用 (FastAPI + 轻量依赖)
├── venv-demucs/             # Demucs 人声分离服务
├── venv-silero/             # Silero VAD 歌词对齐服务
├── venv-rvc/                # RVC 音色克隆服务
├── services/
│   ├── demucs_server.py     # Demucs HTTP 服务
│   ├── silero_server.py     # Silero HTTP 服务
│   └── rvc_server.py        # RVC HTTP 服务
├── backend/
│   └── app/
│       └── main.py          # FastAPI 主应用
├── data/                    # 数据文件
└── models/                  # 模型文件
```

## 启动服务

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

## 内存管理

- 每个服务独立进程，可单独启停
- 不使用时可停止对应服务释放内存
- 建议按需启动：需要哪个模型再启动对应服务
