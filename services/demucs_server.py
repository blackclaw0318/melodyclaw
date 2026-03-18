#!/usr/bin/env python3
"""Demucs 人声分离服务 - 独立进程运行"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import torch
import os
import uuid
from pathlib import Path
import subprocess

app = FastAPI(title="Demucs Service")

# 配置
DEVICE = os.getenv("DEVICE", "cpu")
MODEL_NAME = os.getenv("MODEL_NAME", "htdemucs_ft")
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models/demucs"))

# 全局模型（懒加载）
_model = None


def load_model():
    """懒加载 Demucs 模型"""
    global _model
    if _model is None:
        from demucs.pretrained import get_model
        print(f"[*] 加载 Demucs 模型：{MODEL_NAME} ...")
        _model = get_model(MODEL_NAME)
        _model.to(DEVICE)
        _model.eval()
        print(f"[✓] Demucs 模型已加载到 {DEVICE}")
    return _model


class SeparateRequest(BaseModel):
    song_id: int
    audio_path: str


class SeparateResponse(BaseModel):
    task_id: str
    status: str
    vocals_path: str | None = None
    accompaniment_path: str | None = None
    error: str | None = None


@app.get("/health")
async def health():
    return {"status": "healthy", "device": DEVICE, "model": MODEL_NAME}


@app.post("/separate", response_model=SeparateResponse)
async def separate(request: SeparateRequest):
    """人声分离"""
    task_id = str(uuid.uuid4())
    
    audio_file = DATA_DIR / request.audio_path
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    try:
        print(f"[*] 开始人声分离：{request.audio_path}")
        model = load_model()
        
        from demucs.audio import save_audio
        from torchaudio import load
        
        # 加载音频
        waveform, sr = load(audio_file)
        waveform = waveform.to(DEVICE)
        
        print(f"[*] 音频形状：{waveform.shape}, 采样率：{sr}")
        
        # 推理
        with torch.no_grad():
            sources = model(waveform[None, :])[0]
        
        print(f"[*] 分离完成，输出源数量：{len(sources)}")
        
        # 保存结果
        output_dir = DATA_DIR / "separated" / task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        vocals_path = output_dir / "vocals.wav"
        accompaniment_path = output_dir / "accompaniment.wav"
        
        # vocals: source[0], accompaniment: sum of other sources
        vocals = sources[0]  # 人声
        other = sources[1:].sum(dim=0)  # 伴奏（其他所有音轨之和）
        
        save_audio(vocals, vocals_path, samplerate=sr)
        save_audio(other, accompaniment_path, samplerate=sr)
        
        print(f"[✓] 结果保存到：{vocals_path}, {accompaniment_path}")
        
        return SeparateResponse(
            task_id=task_id,
            status="completed",
            vocals_path=str(vocals_path),
            accompaniment_path=str(accompaniment_path)
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return SeparateResponse(
            task_id=task_id,
            status="failed",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Demucs 人声分离服务")
    print(f"设备：{DEVICE}")
    print(f"模型：{MODEL_NAME}")
    print("端口：8001")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8001)
