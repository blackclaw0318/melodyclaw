#!/usr/bin/env python3
"""RVC 音色克隆服务 - 独立进程运行

核心流程:
1. 加载 Hubert 模型提取源音频特征
2. 加载目标音色模型
3. 特征转换 (源特征 → 目标音色)
4. 使用 Vocoder 生成音频
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
import torch
import numpy as np
from pathlib import Path
import time

app = FastAPI(title="RVC Service")

# ============== 配置 ==============
DEVICE = os.getenv("DEVICE", "cpu")
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models/rvc"))
HUBERT_PATH = MODEL_DIR / "hubert_base_ls960.pt"

# 预设音色配置
PRESET_VOICES = [
    {"id": "pop_male", "name": "流行男声", "style": "温暖明亮", "f0_min": 80, "f0_max": 400},
    {"id": "pop_female", "name": "流行女声", "style": "清澈甜美", "f0_min": 150, "f0_max": 600},
    {"id": "rock_male", "name": "摇滚男声", "style": "粗犷有力", "f0_min": 70, "f0_max": 350},
    {"id": "ballad", "name": "民谣嗓音", "style": "朴实自然", "f0_min": 90, "f0_max": 420},
    {"id": "child", "name": "童声", "style": "稚嫩可爱", "f0_min": 200, "f0_max": 800},
    {"id": "deep", "name": "低沉嗓音", "style": "浑厚磁性", "f0_min": 60, "f0_max": 300},
]

# 全局模型 (懒加载)
_hubert_model = None
_hubert_content = None


# ============== 数据模型 ==============
class VoiceInfo(BaseModel):
    id: str
    name: str
    style: str
    f0_min: int
    f0_max: int


class CloneRequest(BaseModel):
    song_id: int
    vocals_path: str
    voice_id: str
    pitch_shift: int = 0  # 半音偏移 (-12 到 +12)
    f0_method: str = "dio"  # F0 提取方法：dio, pm, harvest


class CloneResponse(BaseModel):
    task_id: str
    status: str
    output_path: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


# ============== Hubert 模型加载 ==============
def load_hubert():
    """懒加载 Hubert 模型"""
    global _hubert_model, _hubert_content
    
    if _hubert_model is None:
        print(f"[*] 加载 Hubert 模型：{HUBERT_PATH} ...")
        start = time.time()
        
        # 加载 checkpoint
        ckpt = torch.load(HUBERT_PATH, map_location=DEVICE, weights_only=False)
        
        # 提取模型权重
        if 'model' in ckpt:
            model_dict = ckpt['model']
        else:
            model_dict = ckpt
        
        _hubert_content = model_dict
        
        load_time = time.time() - start
        print(f"[✓] Hubert 模型已加载到 {DEVICE} ({load_time:.2f}s)")
    
    return _hubert_content


# ============== 音频处理工具函数 ==============
def extract_f0(audio: np.ndarray, sr: int, method: str = "dio", 
               f0_min: float = 50, f0_max: float = 1100) -> np.ndarray:
    """提取音频的基频 (F0)"""
    import pyworld as pw
    
    # 确保音频是 float64
    audio = audio.astype(np.float64)
    
    if method == "dio":
        f0, t = pw.dio(audio, sr, f0_floor=f0_min, f0_ceil=f0_max)
    elif method == "pm":
        f0, t = pw.pm(audio, sr, f0_floor=f0_min, f0_ceil=f0_max)
    elif method == "harvest":
        f0, t = pw.harvest(audio, sr, f0_floor=f0_min, f0_ceil=f0_max)
    else:
        f0, t = pw.dio(audio, sr, f0_floor=f0_min, f0_ceil=f0_max)
    
    # 平滑处理
    f0 = pw.stonemask(audio, f0, t, sr)
    
    return f0


def extract_mel_spectrogram(audio: np.ndarray, sr: int = 22050) -> np.ndarray:
    """提取 Mel 频谱"""
    import librosa
    
    # 确保单声道
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    
    # 提取 Mel 频谱
    mel = librosa.feature.melspectrogram(
        y=audio, 
        sr=sr,
        n_mels=128,
        hop_length=256,
        win_length=1024
    )
    
    # 转换为 log Mel 频谱
    mel = np.log(mel + 1e-8)
    
    return mel


def extract_hubert_features(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
    """使用 Hubert 提取音频特征"""
    import torch.nn.functional as F
    
    hubert_content = load_hubert()
    
    # 获取模型权重
    if isinstance(hubert_content, dict) and 'encoder' in str(type(hubert_content)):
        # 如果是已加载的模型
        pass
    
    # 简化实现：返回音频的统计特征作为占位
    # 实际实现需要完整的 fairseq Hubert 模型推理
    
    # 重采样到 16kHz (如果需要)
    if sr != 16000:
        from scipy import signal
        audio = signal.resample(audio, int(len(audio) * 16000 / sr))
    
    # 归一化
    audio = audio / np.max(np.abs(audio))
    
    # 分帧处理 (Hubert 期望的输入)
    frame_size = 320  # 20ms @ 16kHz
    hop_size = 160    # 10ms
    features = []
    
    for i in range(0, len(audio) - frame_size, hop_size):
        frame = audio[i:i + frame_size]
        # 简化特征：使用 MFCC 作为占位
        import librosa
        mfcc = librosa.feature.mfcc(y=frame, sr=16000, n_mfcc=13)
        features.append(mfcc.mean(axis=1))
    
    return np.array(features)


def pitch_shift_audio(audio: np.ndarray, sr: int, semitones: int) -> np.ndarray:
    """音调变换"""
    import librosa
    
    if semitones == 0:
        return audio
    
    # 使用 librosa 进行音调变换
    shifted = librosa.effects.pitch_shift(audio, sr=sr, n_steps=semitones)
    
    return shifted


def synthesize_audio(features: np.ndarray, f0: np.ndarray, 
                     voice_config: Dict[str, Any]) -> np.ndarray:
    """合成音频 (简化实现)
    
    实际 RVC 实现需要:
    1. 加载预训练的生成器模型
    2. 特征转换
    3. HiFi-GAN vocoder 生成
    
    这里使用简化方法作为占位
    """
    # 简化实现：返回一个合成的正弦波作为占位
    # 实际部署时需要完整的 RVC 模型
    
    sr = 44100
    duration = len(f0) * 0.01  # 假设每帧 10ms
    t = np.linspace(0, duration, int(sr * duration))
    
    # 根据 F0 生成基频
    f0_interp = np.interp(np.linspace(0, len(f0), len(t)), 
                          np.linspace(0, len(f0), len(f0)), 
                          f0)
    f0_interp = np.clip(f0_interp, 50, 1000)
    
    # 生成谐波
    audio = np.zeros_like(t)
    for harmonic in range(1, 6):
        phase = np.cumsum(2 * np.pi * f0_interp * harmonic / sr)
        audio += np.sin(phase) / harmonic
    
    # 添加包络
    envelope = np.ones_like(audio)
    attack = int(0.01 * sr)
    release = int(0.05 * sr)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)
    audio *= envelope
    
    # 归一化
    audio = audio / np.max(np.abs(audio)) * 0.9
    
    return audio.astype(np.float32)


# ============== API 端点 ==============
@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy", 
        "device": DEVICE,
        "hubert_loaded": _hubert_model is not None
    }


@app.get("/voices", response_model=List[VoiceInfo])
async def list_voices():
    """获取预设音色列表"""
    return PRESET_VOICES


@app.post("/clone", response_model=CloneResponse)
async def clone_voice(request: CloneRequest):
    """音色克隆
    
    流程:
    1. 加载源音频 (人声)
    2. 提取 F0 和 Hubert 特征
    3. 应用音调变换
    4. 使用目标音色合成
    5. 保存结果
    """
    task_id = str(uuid.uuid4())
    start_time = time.time()
    
    # 验证文件
    vocals_file = DATA_DIR / request.vocals_path
    if not vocals_file.exists():
        raise HTTPException(status_code=404, detail="人声文件不存在")
    
    # 验证音色
    voice_map = {v["id"]: v for v in PRESET_VOICES}
    if request.voice_id not in voice_map:
        raise HTTPException(
            status_code=400, 
            detail=f"无效的音色 ID，可用：{list(voice_map.keys())}"
        )
    
    voice_config = voice_map[request.voice_id]
    
    try:
        print(f"[*] 开始音色克隆：{request.voice_id}")
        print(f"    输入：{request.vocals_path}")
        print(f"    音调偏移：{request.pitch_shift} 半音")
        
        # 加载音频
        import librosa
        audio, sr = librosa.load(vocals_file, sr=None, mono=True)
        print(f"    音频：{len(audio)/sr:.2f}s @ {sr}kHz")
        
        # 提取 F0
        print(f"    [*] 提取 F0...")
        f0 = extract_f0(
            audio, sr, 
            method=request.f0_method,
            f0_min=voice_config["f0_min"],
            f0_max=voice_config["f0_max"]
        )
        
        # 音调变换
        if request.pitch_shift != 0:
            print(f"    [*] 音调变换：{request.pitch_shift} 半音")
            audio = pitch_shift_audio(audio, sr, request.pitch_shift)
        
        # 提取 Hubert 特征
        print(f"    [*] 提取 Hubert 特征...")
        features = extract_hubert_features(audio, sr)
        
        # 合成音频
        print(f"    [*] 合成音频...")
        output_audio = synthesize_audio(features, f0, voice_config)
        
        # 保存结果
        output_dir = DATA_DIR / "cloned" / task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "cloned_vocals.wav"
        
        # 写入 WAV 文件
        from scipy.io import wavfile
        wavfile.write(str(output_path), 44100, output_audio)
        
        processing_time = time.time() - start_time
        print(f"[✓] 克隆完成：{output_path} ({processing_time:.2f}s)")
        
        return CloneResponse(
            task_id=task_id,
            status="completed",
            output_path=str(output_path),
            processing_time=processing_time
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        processing_time = time.time() - start_time
        return CloneResponse(
            task_id=task_id,
            status="failed",
            error=str(e),
            processing_time=processing_time
        )


@app.post("/features/extract")
async def extract_features(vocals_path: str):
    """提取音频特征 (调试用)"""
    vocals_file = DATA_DIR / vocals_path
    
    if not vocals_file.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        import librosa
        audio, sr = librosa.load(vocals_file, sr=None, mono=True)
        
        f0 = extract_f0(audio, sr)
        features = extract_hubert_features(audio, sr)
        
        return {
            "status": "success",
            "duration": len(audio) / sr,
            "sample_rate": sr,
            "f0_shape": list(f0.shape),
            "f0_min": float(f0[f0 > 0].min()) if (f0 > 0).any() else 0,
            "f0_max": float(f0.max()),
            "features_shape": list(features.shape)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== 主程序 ==============
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("RVC 音色克隆服务")
    print(f"设备：{DEVICE}")
    print(f"Hubert 模型：{HUBERT_PATH}")
    print(f"预设音色：{len(PRESET_VOICES)} 种")
    print("端口：8003")
    print("=" * 50)
    
    # 预加载 Hubert 模型
    load_hubert()
    
    uvicorn.run(app, host="0.0.0.0", port=8003)
