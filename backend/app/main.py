#!/usr/bin/env python3
"""MelodyClaw API - 主应用入口"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os

app = FastAPI(title="MelodyClaw API", version="1.0.0")

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 服务地址
DEMUCS_URL = os.getenv("DEMUCS_URL", "http://localhost:8001")
SILERO_URL = os.getenv("SILERO_URL", "http://localhost:8002")
RVC_URL = os.getenv("RVC_URL", "http://localhost:8003")


class SongResponse(BaseModel):
    id: int
    title: str
    artist: Optional[str] = None
    duration: float
    status: str


class SeparateRequest(BaseModel):
    song_id: int


class SeparateResponse(BaseModel):
    task_id: str
    status: str = "pending"


class LyricsAlignRequest(BaseModel):
    song_id: int
    lyrics: str


class LyricsAlignResponse(BaseModel):
    task_id: str
    status: str = "pending"


class CloneRequest(BaseModel):
    song_id: int
    voice_id: str


class CloneResponse(BaseModel):
    task_id: str
    status: str = "pending"


@app.get("/")
async def root():
    return {
        "service": "MelodyClaw API",
        "status": "running",
        "services": {
            "demucs": DEMUCS_URL,
            "silero": SILERO_URL,
            "rvc": RVC_URL
        }
    }


@app.get("/health")
async def health():
    """健康检查"""
    status = {"api": "healthy"}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in [("demucs", DEMUCS_URL), ("silero", SILERO_URL), ("rvc", RVC_URL)]:
            try:
                resp = await client.get(f"{url}/health")
                status[name] = resp.json()
            except Exception as e:
                status[name] = {"status": "unavailable", "error": str(e)}
    return status


@app.get("/api/v1/songs", response_model=List[SongResponse])
async def list_songs():
    """获取歌曲列表"""
    return []


@app.post("/api/v1/songs/{song_id}/separate", response_model=SeparateResponse)
async def separate_vocals(song_id: int):
    """触发人声分离"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{DEMUCS_URL}/separate",
                json={"song_id": song_id, "audio_path": f"uploads/{song_id}/audio.mp3"},
            )
            resp.raise_for_status()
            data = resp.json()
            return SeparateResponse(task_id=data["task_id"], status=data["status"])
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"Demucs 服务不可用：{str(e)}")


@app.post("/api/v1/lyrics/{song_id}/align", response_model=LyricsAlignResponse)
async def align_lyrics(song_id: int, request: LyricsAlignRequest):
    """歌词时间对齐"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{SILERO_URL}/align",
                json={"song_id": song_id, "audio_path": f"uploads/{song_id}/audio.mp3", "lyrics": request.lyrics},
            )
            resp.raise_for_status()
            data = resp.json()
            return LyricsAlignResponse(task_id=data["task_id"], status=data["status"])
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"Silero 服务不可用：{str(e)}")


@app.post("/api/v1/clone", response_model=CloneResponse)
async def clone_voice(request: CloneRequest):
    """音色克隆"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{RVC_URL}/clone",
                json={"song_id": request.song_id, "vocals_path": f"separated/{request.song_id}/vocals.wav", "voice_id": request.voice_id},
            )
            resp.raise_for_status()
            data = resp.json()
            return CloneResponse(task_id=data["task_id"], status=data["status"])
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"RVC 服务不可用：{str(e)}")


@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    return {"task_id": task_id, "status": "pending", "progress": 0}


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("MelodyClaw API 主服务")
    print("端口：8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
