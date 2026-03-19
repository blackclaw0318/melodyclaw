#!/bin/bash
set -e

echo "Starting MelodyClaw services..."

# 启动 Demucs 服务
echo "[*] Starting Demucs service on port 8001..."
python services/demucs_server.py &

# 启动 Silero 服务
echo "[*] Starting Silero service on port 8002..."
python services/silero_server.py &

# 启动 RVC 服务
echo "[*] Starting RVC service on port 8003..."
python services/rvc_server.py &

# 等待 AI 服务启动
sleep 5

# 启动主 API
echo "[*] Starting Main API on port 8000..."
exec python backend/app/main.py
