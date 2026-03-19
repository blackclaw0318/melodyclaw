FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements-main.txt requirements-demucs.txt requirements-silero.txt requirements-rvc.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    -r requirements-main.txt \
    -r requirements-demucs.txt \
    -r requirements-silero.txt \
    -r requirements-rvc.txt

# 复制应用代码
COPY backend/ ./backend/
COPY services/ ./services/
COPY models/ ./models/

# 创建数据目录
RUN mkdir -p /app/data/{uploads,separated,cloned}

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./melodyclaw.db

EXPOSE 8000 8001 8002 8003

VOLUME ["/app/data"]

# 启动脚本
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
