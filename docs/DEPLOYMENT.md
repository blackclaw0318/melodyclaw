# MelodyClaw Docker 部署指南

## 镜像构建

### 后端服务镜像

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements-*.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements-main.txt

# 复制应用代码
COPY backend/app ./backend/app
COPY services ./services
COPY models ./models

# 创建数据目录
RUN mkdir -p /app/data/{uploads,separated,cloned}

EXPOSE 8000 8001 8002 8003

CMD ["sh", "-c", "\
    python services/demucs_server.py & \
    python services/silero_server.py & \
    python services/rvc_server.py & \
    python backend/app/main.py \
"]
```

### 前端服务镜像

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

## Docker Compose 配置

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

## 快速启动

```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 清理数据
docker-compose down -v
```

## 访问地址

- **前端:** http://localhost:3000
- **API:** http://localhost:8000
- **API 文档:** http://localhost:8000/docs

## 资源限制

建议配置:
- **CPU:** 4 核+
- **内存:** 16GB+
- **存储:** 50GB+

## 生产部署

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name melodyclaw.example.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### HTTPS 配置

```bash
# 使用 Let's Encrypt
certbot --nginx -d melodyclaw.example.com
```
