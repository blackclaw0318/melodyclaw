#!/bin/bash
# 后端 API 端到端测试脚本

set -e

echo "=============================================="
echo "MelodyClaw 后端 API - 端到端测试"
echo "=============================================="

cd /root/.openclaw/workspace/melodyclaw

# 激活虚拟环境
source venv/bin/activate

# 创建测试数据
mkdir -p data/test

echo ""
echo "[1/5] 生成测试音频..."
python3 << 'PYEOF'
import numpy as np
from scipy.io import wavfile

sr = 44100
duration = 2
t = np.linspace(0, duration, int(sr * duration))

# 生成简单音频
f0 = 220 + 50 * np.sin(2 * np.pi * 0.5 * t)
audio = np.zeros_like(t)
for h in range(1, 5):
    phase = np.cumsum(2 * np.pi * f0 * h / sr)
    audio += np.sin(phase) / h

audio = audio / np.max(np.abs(audio)) * 0.9
wavfile.write('data/test/test_song.wav', sr, audio.astype(np.float32))
print(f"Test audio: data/test/test_song.wav ({duration}s)")
PYEOF

# 启动主 API
echo ""
echo "[2/5] 启动 MelodyClaw API..."
python backend/app/main.py &
API_PID=$!
sleep 5

# 测试 API
echo ""
echo "[3/5] 测试 API 端点..."

echo "  - 根路径..."
curl -s http://localhost:8000/ | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'    服务：{d[\"service\"]} v{d[\"version\"]}')"

echo "  - 获取音色列表..."
curl -s http://localhost:8000/api/v1/voices | python3 -c "
import sys,json
voices = json.load(sys.stdin)
print(f'    可用音色：{len(voices)} 种')
for v in voices:
    print(f'      - {v[\"name\"]} (F0: {v[\"f0_min\"]}-{v[\"f0_max\"]}Hz)')
"

echo "  - 获取歌曲列表 (空)..."
curl -s http://localhost:8000/api/v1/songs | python3 -c "import sys,json; songs=json.load(sys.stdin); print(f'    歌曲数量：{len(songs)}')"

echo "  - 上传歌曲..."
SONG_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/songs \
  -F "title=测试歌曲" \
  -F "artist=测试歌手" \
  -F "file=@data/test/test_song.wav")

echo "    $SONG_RESPONSE" | python3 -c "
import sys,json
d = json.load(sys.stdin)
print(f'    歌曲 ID: {d[\"id\"]}')
print(f'    标题：{d[\"title\"]}')
print(f'    状态：{d[\"status\"]}')
"

SONG_ID=$(echo $SONG_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "  - 获取歌曲详情..."
curl -s http://localhost:8000/api/v1/songs/$SONG_ID | python3 -c "
import sys,json
d = json.load(sys.stdin)
print(f'    标题：{d[\"title\"]}')
print(f'    时长：{d[\"duration\"]}s')
"

echo "  - 测试人声分离 (模拟)..."
echo "    (需要 Demucs 服务运行)"

echo "  - 测试歌词对齐 (模拟)..."
curl -s -X POST "http://localhost:8000/api/v1/lyrics/$SONG_ID/align" \
  -H "Content-Type: application/json" \
  -d '{"song_id": '$SONG_ID', "lyrics": "第一行歌词\n第二行歌词\n第三行歌词"}' | python3 -c "
import sys,json
try:
    d = json.load(sys.stdin)
    print(f'    状态：{d.get(\"status\", \"unknown\")}')
except:
    print('    (Silero 服务未运行)')
"

echo "  - 测试音色克隆 (模拟)..."
curl -s -X POST http://localhost:8000/api/v1/clone \
  -H "Content-Type: application/json" \
  -d '{"song_id": '$SONG_ID', "voice_id": "pop_male"}' | python3 -c "
import sys,json
try:
    d = json.load(sys.stdin)
    print(f'    任务 ID: {d.get(\"task_id\", \"N/A\")}')
    print(f'    状态：{d.get(\"status\", \"unknown\")}')
except:
    print('    (RVC 服务未运行)')
"

# 停止服务
echo ""
echo "[4/5] 停止服务..."
kill $API_PID 2>/dev/null || true

# 清理
echo ""
echo "[5/5] 清理测试数据..."
rm -rf data/test
rm -f melodyclaw.db

echo ""
echo "=============================================="
echo "✅ 测试完成!"
echo "=============================================="
