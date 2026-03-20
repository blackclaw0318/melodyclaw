#!/usr/bin/env python3
"""Silero VAD 歌词对齐服务 - 简化版 (避免 JIT 模型兼容性问题)"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from pathlib import Path

app = FastAPI(title="Silero VAD Service")

# 配置
DEVICE = os.getenv("DEVICE", "cpu")
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))


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
    aligned_lyrics: Optional[List[AlignedLine]] = None
    error: Optional[str] = None


@app.get("/health")
async def health():
    return {"status": "healthy", "device": DEVICE}


@app.post("/align", response_model=AlignResponse)
async def align_lyrics(request: AlignRequest):
    """歌词时间对齐 - 简化实现 (均匀分配时间戳)"""
    task_id = str(uuid.uuid4())
    
    audio_file = DATA_DIR / request.audio_path
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    try:
        print(f"[*] 开始歌词对齐：{request.audio_path}")
        
        # 获取音频时长
        from torchaudio import load
        waveform, sr = load(audio_file)
        duration = waveform.shape[1] / sr
        print(f"[*] 音频时长：{duration:.2f}s")
        
        # 解析歌词
        lyrics_lines = [line.strip() for line in request.lyrics.split('\n') if line.strip()]
        print(f"[*] 歌词行数：{len(lyrics_lines)}")
        
        # 均匀分配时间戳
        aligned = []
        if lyrics_lines:
            interval = duration / len(lyrics_lines)
            for i, line in enumerate(lyrics_lines):
                time = (i + 0.5) * interval
                aligned.append(AlignedLine(time=round(time, 2), text=line))
        
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
    print("Silero VAD 歌词对齐服务 (简化版)")
    print(f"设备：{DEVICE}")
    print("端口：8002")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8002)
