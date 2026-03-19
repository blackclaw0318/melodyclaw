#!/usr/bin/env python3
"""模型部署测试脚本 - 验证 CPU 推理可行性"""
import sys
import time
import torch

print("=" * 60)
print("MelodyClaw 模型部署测试")
print(f"Python: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"Device: CPU")
print(f"CPU 核心数：{torch.get_num_threads()}")
print("=" * 60)

# 测试 1: Demucs
print("\n【测试 1】Demucs 人声分离模型")
print("-" * 40)
try:
    start = time.time()
    from demucs.pretrained import get_model
    print("[*] 下载/加载 htdemucs_ft 模型...")
    model = get_model('htdemucs_ft')
    model.to('cpu')
    model.eval()
    load_time = time.time() - start
    print(f"[✓] Demucs 加载成功 ({load_time:.2f}s)")
    
    # 估算内存占用
    param_size = sum(p.numel() * p.element_size() for p in model.parameters()) / 1024 / 1024
    print(f"    模型参数内存：{param_size:.2f} MB")
except Exception as e:
    print(f"[✗] Demucs 失败：{e}")

# 测试 2: Silero VAD
print("\n【测试 2】Silero VAD 语音检测模型")
print("-" * 40)
try:
    start = time.time()
    print("[*] 从 torch hub 加载 Silero VAD...")
    model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=False,
        trust_repo=True
    )
    model.to('cpu')
    model.eval()
    load_time = time.time() - start
    print(f"[✓] Silero VAD 加载成功 ({load_time:.2f}s)")
except Exception as e:
    print(f"[✗] Silero VAD 失败：{e}")

# 测试 3: RVC (检查依赖)
print("\n【测试 3】RVC v2 音色克隆")
print("-" * 40)
try:
    print("[*] 检查 RVC 依赖...")
    import fairseq
    print("    fairseq: ✓")
except ImportError:
    print("    fairseq: ✗ (未安装)")

try:
    import pyworld
    print("    pyworld: ✓")
except ImportError:
    print("    pyworld: ✗ (未安装)")

try:
    from fairseq import checkpoint_utils
    print("[*] 尝试加载 Hubert 模型...")
    # Hubert 模型路径
    hubert_path = "/root/.openclaw/workspace/melodyclaw/models/rvc/hubert_base.pt"
    import os
    if os.path.exists(hubert_path):
        print(f"    Hubert 模型文件存在：{hubert_path}")
    else:
        print(f"    Hubert 模型文件不存在，需要下载")
except Exception as e:
    print(f"[✗] Hubert 加载失败：{e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
