#!/bin/bash
# RVC 服务端到端测试脚本

set -e

echo "=============================================="
echo "RVC 音色克隆服务 - 端到端测试"
echo "=============================================="

cd /root/.openclaw/workspace/melodyclaw

# 激活虚拟环境
source venv-rvc/bin/activate

# 创建测试数据目录
mkdir -p data/test
mkdir -p data/cloned

# 生成测试音频 (3 秒正弦波)
echo ""
echo "[1/4] 生成测试音频..."
python3 << 'PYEOF'
import numpy as np
from scipy.io import wavfile

sr = 44100
duration = 3
t = np.linspace(0, duration, int(sr * duration))

f0_base = 200
f0_mod = 50 * np.sin(2 * np.pi * 0.5 * t)
f0 = f0_base + f0_mod

audio = np.zeros_like(t)
for harmonic in range(1, 6):
    phase = np.cumsum(2 * np.pi * f0 * harmonic / sr)
    audio += np.sin(phase) / harmonic

envelope = np.ones_like(audio)
attack = int(0.01 * sr)
release = int(0.05 * sr)
envelope[:attack] = np.linspace(0, 1, attack)
envelope[-release:] = np.linspace(1, 0, release)
audio *= envelope

audio = audio / np.max(np.abs(audio)) * 0.9
wavfile.write('data/test/test_vocals.wav', sr, audio.astype(np.float32))
print(f"Test audio generated: data/test/test_vocals.wav ({duration}s)")
PYEOF

# 启动 RVC 服务
echo ""
echo "[2/4] 启动 RVC 服务..."
python services/rvc_server.py &
RVC_PID=$!
sleep 5

# 测试 API
echo ""
echo "[3/4] 测试 API 端点..."

echo "  Health check:"
curl -s http://localhost:8003/health
echo ""

echo "  Voice list:"
curl -s http://localhost:8003/voices
echo ""

echo "  Clone test (pop_male):"
curl -s -X POST http://localhost:8003/clone \
  -H "Content-Type: application/json" \
  -d '{"song_id": 1, "vocals_path": "test/test_vocals.wav", "voice_id": "pop_male", "pitch_shift": 0}'
echo ""

# 停止服务
echo ""
echo "[4/4] 停止服务..."
kill $RVC_PID 2>/dev/null || true

echo ""
echo "=============================================="
echo "Test complete!"
echo "=============================================="
