# MelodyClaw V2.0 - 详细实现方案

> 基于需求文档的技术实施方案  
> 版本：2.0 | 日期：2026-03-23  
> 分支：`blackclaw_0323`

---

## 📋 目录

1. [开发环境搭建](#1-开发环境搭建)
2. [前端实现方案](#2-前端实现方案)
3. [后端实现方案](#3-后端实现方案)
4. [数据库设计](#4-数据库设计)
5. [API 接口规范](#5-api 接口规范)
6. [部署方案](#6-部署方案)
7. [测试方案](#7-测试方案)
8. [性能优化](#8-性能优化)

---

## 1. 开发环境搭建

### 1.1 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4 核 | 8 核 |
| 内存 | 8GB | 16GB |
| 存储 | 20GB | 50GB SSD |
| Node.js | 18.x | 20.x LTS |
| Python | 3.10+ | 3.12 |

### 1.2 环境初始化

```bash
# 1. 克隆项目
git clone https://github.com/blackclaw0318/melodyclaw.git
cd melodyclaw

# 2. 安装前端依赖
cd frontend
npm install

# 3. 创建 Python 虚拟环境
cd ..
python3 -m venv venv
source venv/bin/activate

# 4. 安装后端依赖
pip install -r requirements.txt
```

### 1.3 开发工具

- **IDE**: VS Code / WebStorm / PyCharm
- **数据库工具**: DB Browser for SQLite
- **API 测试**: Postman / Insomnia
- **浏览器**: Chrome DevTools

---

## 2. 前端实现方案

### 2.1 技术选型

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | Vue 3 | 3.4+ | Composition API |
| 构建 | Vite | 5.x | 快速开发服务器 |
| 样式 | TailwindCSS | 4.x | 原子化 CSS |
| 状态 | Pinia | 2.x | 轻量级状态管理 |
| 路由 | Vue Router | 4.x | SPA 路由 |
| HTTP | Axios | 1.x | API 客户端 |

### 2.2 核心功能实现

#### 2.2.1 摄像头调用

```javascript
// composables/useCamera.js
export function useCamera() {
  const startCamera = async (facingMode = 'environment') => {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { 
        facingMode,
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      },
      audio: {
        echoCancellation: true,
        noiseSuppression: true
      }
    });
    return stream;
  };
  
  return { startCamera };
}
```

**关键点**:
- 优先使用后置摄像头 (`environment`)
- 开启音频降噪和回声消除
- 错误处理：权限拒绝、设备不存在

#### 2.2.2 拖拽功能

```javascript
// composables/useDraggable.js
export function useDraggable({ initialX, initialY, onDrag }) {
  const x = ref(initialX);
  const y = ref(initialY);
  let isDragging = false;

  const startDrag = (e) => {
    isDragging = true;
    const startX = e.clientX || e.touches[0].clientX;
    const startY = e.clientY || e.touches[0].clientY;
    const startLeft = x.value;
    const startTop = y.value;

    const onMove = (moveEvent) => {
      if (!isDragging) return;
      const clientX = moveEvent.clientX || moveEvent.touches[0].clientX;
      const clientY = moveEvent.clientY || moveEvent.touches[0].clientY;
      x.value = startLeft + (clientX - startX);
      y.value = startTop + (clientY - startY);
      onDrag?.({ x: x.value, y: y.value });
    };

    const onEnd = () => { isDragging = false; };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onEnd);
    document.addEventListener('touchmove', onMove);
    document.addEventListener('touchend', onEnd);
  };

  return { x, y, startDrag };
}
```

#### 2.2.3 录制功能

```javascript
// composables/useRecorder.js
export function useRecorder() {
  const startRecording = async ({ cameraStream, accompanimentUrl }) => {
    // 1. 混合音频流
    const audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(cameraStream);
    
    // 2. 创建 MediaRecorder
    const recorder = new MediaRecorder(cameraStream, {
      mimeType: 'video/webm;codecs=vp9,opus',
      videoBitsPerSecond: 2500000
    });
    
    const chunks = [];
    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.start(1000);
    
    return { recorder, chunks };
  };
  
  return { startRecording };
}
```

### 2.3 页面结构

```
src/views/
├── Home.vue          # 歌曲列表页
├── Record.vue        # 拍摄页
├── Preview.vue       # 预览页
└── Profile.vue       # 个人页 (P2)
```

---

## 3. 后端实现方案

### 3.1 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 异步高性能 |
| 服务器 | Uvicorn | ASGI 服务器 |
| ORM | SQLAlchemy | 数据库操作 |
| 验证 | Pydantic | 数据验证 |
| 视频处理 | FFmpeg | 转码/合并 |

### 3.2 项目结构

```
backend/
├── app/
│   ├── main.py           # 应用入口
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   ├── models.py         # 数据模型
│   ├── schemas.py        # Pydantic 模型
│   └── routes/
│       ├── songs.py      # 歌曲路由
│       └── recordings.py # 作品路由
├── services/
│   ├── song_service.py   # 歌曲业务逻辑
│   └── video_service.py  # 视频处理
├── uploads/              # 上传文件
└── requirements.txt
```

### 3.3 核心 API 实现

```python
# app/routes/recordings.py
from fastapi import APIRouter, UploadFile, File, Form
from app.models import RecordingV2
from app.database import get_db
import uuid

router = APIRouter(prefix="/api/v2/recordings")

@router.post("")
async def create_recording(
    song_id: int = Form(...),
    video: UploadFile = File(...),
    lobster_position: str = Form(None),
    lyrics_position: str = Form(None),
    db = Depends(get_db)
):
    # 1. 保存视频文件
    filename = f"{uuid.uuid4().hex}.webm"
    filepath = f"uploads/{filename}"
    
    with open(filepath, "wb") as f:
        content = await video.read()
        f.write(content)
    
    # 2. 创建数据库记录
    recording = RecordingV2(
        uuid=uuid.uuid4().hex,
        song_id=song_id,
        video_file=filepath,
        lobster_position=json.loads(lobster_position) if lobster_position else None,
        lyrics_position=json.loads(lyrics_position) if lyrics_position else None
    )
    db.add(recording)
    db.commit()
    db.refresh(recording)
    
    return recording
```

---

## 4. 数据库设计

### 4.1 ER 图

```
┌─────────────┐       ┌─────────────────┐
│   songs_v2  │       │  recordings_v2  │
├─────────────┤       ├─────────────────┤
│ id (PK)     │───┐   │ id (PK)         │
│ title       │   └──▶│ song_id (FK)    │
│ artist      │       │ uuid (UNIQUE)   │
│ bpm         │       │ video_file      │
│ duration    │       │ lobster_position│
│ cover_file  │       │ lyrics_position │
│ ...         │       │ view_count      │
└─────────────┘       │ like_count      │
                      │ created_at      │
                      └─────────────────┘
```

### 4.2 表结构

```sql
-- 歌曲表
CREATE TABLE songs_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    bpm INTEGER,
    duration FLOAT,
    cover_file VARCHAR(512),
    accompaniment_file VARCHAR(512),
    lyrics TEXT,
    category VARCHAR(64),
    duet_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 作品表
CREATE TABLE recordings_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid VARCHAR(64) UNIQUE NOT NULL,
    song_id INTEGER NOT NULL,
    video_file VARCHAR(512) NOT NULL,
    thumbnail_file VARCHAR(512),
    duration FLOAT,
    lobster_position JSON,
    lyrics_position JSON,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs_v2(id)
);
```

---

## 5. API 接口规范

### 5.1 基础 URL

- 开发环境：`http://localhost:8000/api/v2`
- 生产环境：`https://api.melodyclaw.com/api/v2`

### 5.2 接口列表

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/songs` | 获取歌曲列表 | 否 |
| GET | `/songs/{id}` | 获取歌曲详情 | 否 |
| GET | `/songs/{id}/accompaniment` | 获取伴奏 | 否 |
| POST | `/recordings` | 上传作品 | 否 |
| GET | `/recordings` | 作品列表 | 否 |
| GET | `/recordings/{id}` | 作品详情 | 否 |
| GET | `/recordings/{id}/video` | 下载视频 | 否 |
| DELETE | `/recordings/{id}` | 删除作品 | 是 |
| POST | `/recordings/{id}/like` | 点赞 | 否 |

### 5.3 响应格式

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

错误响应：

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [ ... ]
  }
}
```

---

## 6. 部署方案

### 6.1 Docker 部署（推荐）

**后端镜像** (`Dockerfile.backend`):

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*
COPY requirements-*.txt ./
RUN pip install --no-cache-dir -r requirements-main.txt
COPY backend/app ./backend/app
COPY services ./services
RUN mkdir -p /app/data/{uploads,separated,cloned}
EXPOSE 8000 8001 8002 8003
CMD ["sh", "-c", "python services/demucs_server.py & python services/silero_server.py & python services/rvc_server.py & python backend/app/main.py"]
```

**前端镜像** (`Dockerfile.frontend`):

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**Docker Compose** (`docker-compose.yml`):

```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
      - "8001:8001"
      - "8002:8002"
      - "8003:8003"
    volumes:
      - melodyclaw-data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./melodyclaw.db
    deploy:
      resources:
        limits:
          memory: 12G
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
volumes:
  melodyclaw-data:
```

### 6.2 部署步骤

```bash
# 1. 构建并启动
docker-compose up -d --build

# 2. 查看日志
docker-compose logs -f

# 3. 停止服务
docker-compose down

# 4. 清理数据（可选）
docker-compose down -v
```

### 6.3 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

### 6.4 生产环境

**Nginx 反向代理**:

```nginx
server {
    listen 80;
    server_name melodyclaw.example.com;
    location / { proxy_pass http://localhost:3000; }
    location /api { proxy_pass http://localhost:8000; }
}
```

**HTTPS 配置**:

```bash
certbot --nginx -d melodyclaw.example.com
```

**资源要求**:
- CPU: 4 核+
- 内存：16GB+
- 存储：50GB+

---

## 7. 测试方案

### 7.1 测试类型

| 类型 | 工具 | 覆盖率目标 |
|------|------|------------|
| 单元测试 | Vitest + Pytest | 80%+ |
| 集成测试 | Pytest | 核心流程 100% |
| E2E 测试 | Playwright | 关键路径 100% |

### 7.2 测试命令

```bash
# 前端测试
cd frontend && npm run test

# 后端测试
source venv/bin/activate && pytest

# E2E 测试
python tests/e2e/test_recording.py
```

---

## 8. 性能优化

### 8.1 前端优化

| 优化项 | 方案 | 预期提升 |
|--------|------|----------|
| 首屏加载 | 路由懒加载 | -40% |
| 图片加载 | 懒加载 + WebP | -60% |
| 动画性能 | Canvas + RAF | 60fps |
| 缓存 | Service Worker | 离线可用 |

### 8.2 后端优化

| 优化项 | 方案 | 预期提升 |
|--------|------|----------|
| 视频转码 | 异步任务队列 | 响应<200ms |
| 文件存储 | CDN 分发 | 加载<1s |
| 数据库 | 索引优化 | 查询<50ms |
| 缓存 | Redis | 命中率>80% |

---

## 9. 开发里程碑

| 阶段 | 任务 | 预计时间 | 状态 |
|------|------|----------|------|
| 1 | 前端基础框架 | 2 天 | ⏳ |
| 2 | 核心组件开发 | 3 天 | ⏳ |
| 3 | 后端 API 开发 | 2 天 | ⏳ |
| 4 | 集成测试 | 1 天 | ⏳ |
| 5 | 性能优化 | 1 天 | ⏳ |
| 6 | 部署上线 | 0.5 天 | ⏳ |

**总计**: 9.5 天

---

## 附录

### A. 参考资料

- [Vue 3 官方文档](https://vuejs.org/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [MediaDevices API](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices)

### B. 常见问题

**Q: 摄像头无法启动？**
A: 检查浏览器权限设置，确保使用 HTTPS 或 localhost。

**Q: 视频文件过大？**
A: 调整录制码率，使用 FFmpeg 转码压缩。

**Q: 动画卡顿？**
A: 使用 Canvas 渲染，避免 DOM 操作。

---

**文档状态**: 正式发布  
**维护者**: blackclaw0318
