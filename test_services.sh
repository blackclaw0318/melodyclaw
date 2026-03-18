#!/bin/bash
# MelodyClaw 服务测试脚本

set -e

echo "========================================"
echo "MelodyClaw 服务测试"
echo "========================================"

# 测试音频路径
TEST_AUDIO="data/uploads/test/test_audio.mp3"

# 1. 启动 Demucs 服务
echo ""
echo "[1/4] 启动 Demucs 服务 (端口 8001)..."
source venv-demucs/bin/activate
python services/demucs_server.py &
DEMUCS_PID=$!
sleep 3

# 2. 启动 Silero 服务
echo ""
echo "[2/4] 启动 Silero 服务 (端口 8002)..."
source venv-silero/bin/activate
python services/silero_server.py &
SILERO_PID=$!
sleep 3

# 3. 启动主 API
echo ""
echo "[3/4] 启动主 API (端口 8000)..."
source venv/bin/activate
python backend/app/main.py &
API_PID=$!
sleep 3

# 4. 健康检查
echo ""
echo "[4/4] 健康检查..."
sleep 2

echo ""
echo "检查 Demucs 服务..."
curl -s http://localhost:8001/health | python3 -m json.tool

echo ""
echo "检查 Silero 服务..."
curl -s http://localhost:8002/health | python3 -m json.tool

echo ""
echo "检查主 API..."
curl -s http://localhost:8000/health | python3 -m json.tool

# 5. 测试人声分离
echo ""
echo "========================================"
echo "测试人声分离..."
echo "========================================"

if [ -f "$TEST_AUDIO" ]; then
    echo "测试音频：$TEST_AUDIO"
    
    # 调用 Demucs API
    RESPONSE=$(curl -s -X POST http://localhost:8001/separate \
        -H "Content-Type: application/json" \
        -d "{\"song_id\": 1, \"audio_path\": \"$TEST_AUDIO\"}")
    
    echo "响应:"
    echo "$RESPONSE" | python3 -m json.tool
else
    echo "错误：测试音频不存在"
fi

# 清理
echo ""
echo "========================================"
echo "停止服务..."
echo "========================================"
kill $DEMUCS_PID $SILERO_PID $API_PID 2>/dev/null || true
echo "完成"
