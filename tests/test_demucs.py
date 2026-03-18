#!/usr/bin/env python3
"""Demucs 人声分离模型 CPU 推理测试"""

import torch
import time
import warnings
warnings.filterwarnings("ignore")

print("=" * 50)
print("Demucs 人声分离模型 - CPU 推理测试")
print("=" * 50)

# 检查设备
device = torch.device("cpu")
print(f"\n[1] 设备检查：{device}")
print(f"    CUDA 可用：{torch.cuda.is_available()}")

# 加载 Demucs 模型
print("\n[2] 加载 Demucs htdemucs_ft 模型...")
start = time.time()
try:
    from demucs.pretrained import get_model
    model = get_model('htdemucs_ft')
    model.to(device)
    model.eval()
    load_time = time.time() - start
    print(f"    ✓ 模型加载完成 ({load_time:.2f}s)")
    print(f"    模型设备：{next(model.parameters()).device}")
except Exception as e:
    print(f"    ✗ 模型加载失败：{e}")
    exit(1)

# 创建测试音频（3 秒静音）
print("\n[3] 创建测试音频...")
import numpy as np
sample_rate = 44100
duration = 3  # 秒
test_audio = torch.randn(1, 2, sample_rate * duration).to(device)  # 立体声
print(f"    音频形状：{test_audio.shape}")
print(f"    时长：{duration}秒")

# 推理测试
print("\n[4] 执行推理测试...")
start = time.time()
try:
    with torch.no_grad():
        ref = model(ref=test_audio)
    infer_time = time.time() - start
    print(f"    ✓ 推理完成 ({infer_time:.2f}s)")
    print(f"    实时率：{infer_time/duration:.2f}x")
    
    # 输出形状
    if isinstance(ref, (list, tuple)):
        print(f"    输出源数量：{len(ref)}")
        for i, src in enumerate(ref):
            print(f"      源{i}: {src.shape}")
except Exception as e:
    print(f"    ✗ 推理失败：{e}")
    exit(1)

# 内存使用
print("\n[5] 内存使用估算...")
import os
process = os.popen('ps -o rss= -p %d' % os.getpid())
rss_kb = int(process.read().strip())
process.close()
rss_mb = rss_kb / 1024
print(f"    当前进程内存：{rss_mb:.1f}MB")

print("\n" + "=" * 50)
print("✓ Demucs CPU 推理测试通过")
print("=" * 50)
