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
duration = 3  # 3 秒
t = np.linspace(0, duration, int(sr * duration))

# 生成带有基频变化的音频 (模拟人声)
f0_base = 200  # 基频 200Hz
f0_mod = 50 * np.sin(2 * np.pi * 0.5 * t)  # 0.5Hz 调制
f0 = f0_base + f0_mod

# 生成谐波
audio = np.zeros_like(t)
for harmonic in range(1, 6):
    phase = np.cumsum(2 * np.pi * f0 * harmonic / sr)
    audio += np.sin(phase) / harmonic

# 添加包络
envelope = np.ones_like(audio)
attack = int(0.01 * sr)
release = int(0.05 * sr)
envelope[:attack] = np.linspace(0, 1, attack)
envelope[-release:] = np.linspace(1, 0, release)
audio *= envelope

# 归一化并保存
audio = audio / np.max(np.abs(audio)) * 0.9
wavfile.write('data/test/test_vocals.wav', sr, audio.astype(np.float32))

print(f"✓ 测试音频已生成：data/test/test_vocals.wav")
print(f"  时长：{duration}s, 采样率：{sr}Hz")
PYEOF

# 启动 RVC 服务
echo ""
echo "[2/4] 启动 RVC 服务..."
python services/rvc_server.py &
RVC_PID=$!
sleep 3

# 检查服务状态
echo ""
echo "[3/4] 测试 API 端点..."

# 健康检查
echo "  - 健康检查..."
HEALTH=$(curl -s http://localhost:8003/health)
echo "    $HEALTH"

# 获取音色列表
echo "  - 获取音色列表..."
curl -s http://localhost:8003/voices | python3 -c "import sys,json; voices=json.load(sys.stdin); print(f'    可用音色：{len(voices)} 种'); [print(f'      - {v[\"name\"]} ({v[\"id\"]})') for v in voices]"

# 测试音色克隆
echo ""
echo "  - 测试音色克隆 (流行男声)..."
CLONE_RESULT=$(curl -s -X POST http://localhost:8003/clone \
  -H "Content-Type: application/json" \
  -d '{"song_id": 1, "vocals_path": "test/test_vocals.wav", "voice_id": "pop_male", "pitch_shift": 0}')

echo "    $CLONE_RESULT" | python3 -c "
import sys, json
result = json.load(sys.stdin)
print(f'    任务 ID: {result[\"task_id\"]}')
print(f'    状态：{result[\"status\"]}')
if result.get('output_path'):
    print(f'    输出：{result[\"output_path\"]}')
if result.get('processing_time'):
    print(f'    耗时：{result[\"processing_time\"]:.2f}s')
if result.get('error'):
    print(f'    错误：{result[\"error\"]}')
"

# 停止服务
echo ""
echo "[4/4] 停止服务..."
kill $RVC_PID 2>/dev/null || true
wait $RVC_PID 2>/dev/null || true

echo ""
echo "=============================================="
echo "✅ 测试完成!"
echo "=============================================="
