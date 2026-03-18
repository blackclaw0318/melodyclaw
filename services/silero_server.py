#!/usr/bin/env python3
"""Silero VAD 歌词对齐服务 - 独立进程运行"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import torch
import os
import uuid
from pathlib import Path

app = FastAPI(title="Silero VAD Service")

# 配置
DEVICE = os.getenv("DEVICE", "cpu")
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

# 全局模型（懒加载）
_model = None
_utils = None


def load_model():
    """懒加载 Silero VAD 模型"""
    global _model, _utils
    if _model is None:
        print(f"[*] 加载 Silero VAD 模型...")
        _model, _utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True
        )
        _model.to(DEVICE)
        _model.eval()
        print(f"[✓] Silero VAD 模型已加载到 {DEVICE}")
    return _model, _utils


class AlignedLine(BaseModel):
    time: float
    text: str


class AlignRequest(BaseModel):
    song_id: int
    audio_path: str
    lyrics: str


class AlignResponse(BaseModel):
    task_id: str
    status: str
    aligned_lyrics: List[AlignedLine] | None = None
    error: str | None = None


@app.get("/health")
async def health():
    return {"status": "healthy", "device": DEVICE}


@app.post("/align", response_model=AlignResponse)
async def align_lyrics(request: AlignRequest):
    """歌词时间对齐"""
    task_id = str(uuid.uuid4())
    
    audio_file = DATA_DIR / request.audio_path
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    try:
        print(f"[*] 开始歌词对齐：{request.audio_path}")
        model, utils = load_model()
        get_speech_timestamps = utils[0]
        
        from torchaudio import load
        waveform, sr = load(audio_file)
        waveform = waveform.to(DEVICE)
        
        # 立体声转单声道
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        
        # 检测语音活动时间戳
        with torch.no_grad():
            speech_timestamps = get_speech_timestamps(
                waveform.cpu().squeeze(),
                model,
                sampling_rate=sr,
                min_speech_duration_ms=500,
                min_silence_duration_ms=300
            )
        
        # 解析歌词
        lyrics_lines = [line.strip() for line in request.lyrics.split('\n') if line.strip()]
        
        # 对齐歌词
        aligned = []
        total_duration = len(waveform[0]) / sr
        
        if speech_timestamps and lyrics_lines:
            timestamps = []
            for ts in speech_timestamps:
                start_sec = ts['start'] / sr
                end_sec = ts['end'] / sr
                timestamps.append((start_sec + end_sec) / 2)
            
            for i, ts in enumerate(timestamps[:len(lyrics_lines)]):
                aligned.append(AlignedLine(time=round(ts, 2), text=lyrics_lines[i]))
            
            if len(lyrics_lines) > len(timestamps):
                interval = total_duration / (len(lyrics_lines) - len(timestamps) + 1)
                for i, line in enumerate(lyrics_lines[len(timestamps):], start=len(timestamps)):
                    aligned.append(AlignedLine(time=round(timestamps[-1] + (i - len(timestamps) + 1) * interval, 2), text=line))
        else:
            interval = total_duration / max(len(lyrics_lines), 1)
            for i, line in enumerate(lyrics_lines):
                aligned.append(AlignedLine(time=round(i * interval, 2), text=line))
        
        print(f"[✓] 对齐完成，共 {len(aligned)} 句歌词")
        
        return AlignResponse(
            task_id=task_id,
            status="completed",
            aligned_lyrics=aligned
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return AlignResponse(
            task_id=task_id,
            status="failed",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Silero VAD 歌词对齐服务")
    print(f"设备：{DEVICE}")
    print("端口：8002")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8002)
