# MelodyClaw 端到端集成测试

## 测试环境
- **系统:** Ubuntu 22.04
- **CPU:** 4 核
- **内存:** 16GB
- **Python:** 3.12.3
- **Node.js:** v22.22.1

## 测试流程

### 1. 启动所有服务

```bash
cd /root/.openclaw/workspace/melodyclaw

# 启动 Demucs 服务 (端口 8001)
source venv-demucs/bin/activate
python services/demucs_server.py &

# 启动 Silero 服务 (端口 8002)
source venv-silero/bin/activate
python services/silero_server.py &

# 启动 RVC 服务 (端口 8003)
source venv-rvc/bin/activate
python services/rvc_server.py &

# 启动主 API (端口 8000)
source venv/bin/activate
cd backend/app
python main.py &

# 启动前端 (端口 3000)
cd ../../frontend
npm run dev &
```

### 2. 健康检查

```bash
# 检查主 API
curl http://localhost:8000/health

# 检查 Demucs
curl http://localhost:8001/health

# 检查 Silero
curl http://localhost:8002/health

# 检查 RVC
curl http://localhost:8003/health
```

### 3. 完整流程测试

1. **上传歌曲** - POST /api/v1/songs
2. **人声分离** - POST /api/v1/songs/{id}/separate
3. **歌词对齐** - POST /api/v1/lyrics/{id}/align
4. **音色克隆** - POST /api/v1/clone
5. **下载结果** - GET /api/v1/cloned/{task_id}/download

### 4. 性能基准

| 操作 | 输入 | 预期时间 | 实测时间 |
|------|------|----------|----------|
| 人声分离 | 3 分钟音频 | ~3 分钟 | - |
| 歌词对齐 | 3 分钟音频 | ~30 秒 | - |
| 音色克隆 | 3 分钟人声 | ~4 分钟 | - |

## 通过标准

- [ ] 所有服务健康检查通过
- [ ] 完整流程无错误
- [ ] 内存占用 < 12GB
- [ ] 前端页面正常渲染
