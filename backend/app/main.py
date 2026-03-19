#!/usr/bin/env python3
"""MelodyClaw API - 主应用入口

功能:
- 歌曲管理 (上传/列表/删除)
- 人声分离 (调用 Demucs 服务)
- 歌词对齐 (调用 Silero 服务)
- 音色克隆 (调用 RVC 服务)
- 任务管理
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
import shutil
import httpx
from datetime import datetime
from pathlib import Path

from database import get_db, init_db, engine
from models import Base, Song, CloneTask, PresetVoice, SongStatus, TaskStatus

# ============== 配置 ==============
app = FastAPI(title="MelodyClaw API", version="1.0.0", description="歌声克隆系统 API")

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

# 数据目录
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
UPLOAD_DIR = DATA_DIR / "uploads"
SEPARATED_DIR = DATA_DIR / "separated"
CLONED_DIR = DATA_DIR / "cloned"

# 确保目录存在
for dir_path in [DATA_DIR, UPLOAD_DIR, SEPARATED_DIR, CLONED_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# ============== 数据模型 ==============
class SongCreate(BaseModel):
    title: str
    artist: Optional[str] = None


class SongResponse(BaseModel):
    id: int
    title: str
    artist: Optional[str] = None
    duration: Optional[float] = None
    status: str
    created_at: Optional[str] = None
    has_vocals: bool = False
    has_accompaniment: bool = False
    has_aligned_lyrics: bool = False
    has_cloned: bool = False


class SeparateRequest(BaseModel):
    song_id: int


class SeparateResponse(BaseModel):
    task_id: str
    status: str
    vocals_path: Optional[str] = None
    accompaniment_path: Optional[str] = None


class LyricsAlignRequest(BaseModel):
    song_id: int
    lyrics: str


class AlignedLine(BaseModel):
    time: float
    text: str


class LyricsAlignResponse(BaseModel):
    task_id: str
    status: str
    aligned_lyrics: Optional[List[AlignedLine]] = None


class CloneRequest(BaseModel):
    song_id: int
    voice_id: str
    pitch_shift: int = 0
    f0_method: str = "dio"


class CloneResponse(BaseModel):
    task_id: str
    status: str
    output_path: Optional[str] = None
    processing_time: Optional[float] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    song_id: int
    voice_id: str
    status: str
    progress: int
    error_message: Optional[str] = None
    output_file: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: str
    completed_at: Optional[str] = None


class VoiceInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    style: Optional[str] = None
    f0_min: int
    f0_max: int


# ============== API 端点 ==============
@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    print("[*] 初始化数据库...")
    init_db()
    print("[✓] 启动完成")


@app.get("/")
async def root():
    return {
        "service": "MelodyClaw API",
        "version": "1.0.0",
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


# ============== 歌曲管理 ==============
@app.post("/api/v1/songs", response_model=SongResponse)
async def create_song(
    title: str = Form(...),
    artist: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传歌曲"""
    # 保存上传文件
    song_id = str(uuid.uuid4())
    song_dir = UPLOAD_DIR / song_id
    song_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]:
        raise HTTPException(status_code=400, detail=f"不支持的音频格式：{file_ext}")
    
    file_path = song_dir / f"audio{file_ext}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 获取音频时长
    duration = None
    try:
        import librosa
        y, sr = librosa.load(str(file_path), sr=None)
        duration = len(y) / sr
    except Exception:
        pass
    
    # 创建数据库记录
    song = Song(
        title=title,
        artist=artist,
        original_file=str(file_path),
        duration=duration,
        status=SongStatus.UPLOADED
    )
    db.add(song)
    db.commit()
    db.refresh(song)
    
    return SongResponse(**song.to_dict())


@app.get("/api/v1/songs", response_model=List[SongResponse])
async def list_songs(db: Session = Depends(get_db)):
    """获取歌曲列表"""
    songs = db.query(Song).order_by(Song.created_at.desc()).all()
    return [SongResponse(**song.to_dict()) for song in songs]


@app.get("/api/v1/songs/{song_id}", response_model=SongResponse)
async def get_song(song_id: int, db: Session = Depends(get_db)):
    """获取歌曲详情"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    return SongResponse(**song.to_dict())


@app.delete("/api/v1/songs/{song_id}")
async def delete_song(song_id: int, db: Session = Depends(get_db)):
    """删除歌曲"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    
    # 删除文件
    try:
        for file_path in [song.original_file, song.vocals_file, song.accompaniment_file, song.cloned_file]:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"删除文件失败：{e}")
    
    # 删除数据库记录
    db.delete(song)
    db.commit()
    
    return {"status": "deleted", "song_id": song_id}


@app.get("/api/v1/songs/{song_id}/download")
async def download_song(song_id: int, db: Session = Depends(get_db)):
    """下载原始音频"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    if not song.original_file or not os.path.exists(song.original_file):
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    return FileResponse(
        song.original_file,
        media_type="audio/mpeg",
        filename=Path(song.original_file).name
    )


# ============== 人声分离 ==============
@app.post("/api/v1/songs/{song_id}/separate", response_model=SeparateResponse)
async def separate_vocals(song_id: int, db: Session = Depends(get_db)):
    """触发人声分离"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    if not song.original_file or not os.path.exists(song.original_file):
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    # 计算相对路径
    audio_path = str(Path(song.original_file).relative_to(DATA_DIR))
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                f"{DEMUCS_URL}/separate",
                json={"song_id": song_id, "audio_path": audio_path},
            )
            resp.raise_for_status()
            data = resp.json()
            
            # 更新歌曲状态
            if data.get("status") == "completed":
                song.status = SongStatus.SEPARATED
                song.vocals_file = data.get("vocals_path")
                song.accompaniment_file = data.get("accompaniment_path")
                song.separate_task_id = data.get("task_id")
                db.commit()
            
            return SeparateResponse(**data)
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"Demucs 服务不可用：{str(e)}")


# ============== 歌词对齐 ==============
@app.post("/api/v1/lyrics/{song_id}/align", response_model=LyricsAlignResponse)
async def align_lyrics(song_id: int, request: LyricsAlignRequest, db: Session = Depends(get_db)):
    """歌词时间对齐"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    if not song.original_file or not os.path.exists(song.original_file):
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    # 计算相对路径
    audio_path = str(Path(song.original_file).relative_to(DATA_DIR))
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                f"{SILERO_URL}/align",
                json={"song_id": song_id, "audio_path": audio_path, "lyrics": request.lyrics},
            )
            resp.raise_for_status()
            data = resp.json()
            
            # 更新歌曲状态
            if data.get("status") == "completed":
                import json
                song.aligned_lyrics = json.dumps([line.dict() for line in data.get("aligned_lyrics", [])])
                song.status = SongStatus.ALIGNED
                song.align_task_id = data.get("task_id")
                db.commit()
            
            return LyricsAlignResponse(**data)
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"Silero 服务不可用：{str(e)}")


# ============== 音色克隆 ==============
@app.get("/api/v1/voices", response_model=List[VoiceInfo])
async def list_voices(db: Session = Depends(get_db)):
    """获取预设音色列表"""
    voices = db.query(PresetVoice).filter(PresetVoice.is_active == 1).all()
    return [VoiceInfo(**voice.to_dict()) for voice in voices]


@app.post("/api/v1/clone", response_model=CloneResponse)
async def clone_voice(request: CloneRequest, db: Session = Depends(get_db)):
    """音色克隆"""
    song = db.query(Song).filter(Song.id == request.song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    if not song.vocals_file or not os.path.exists(song.vocals_file):
        raise HTTPException(status_code=404, detail="人声文件不存在，请先进行人声分离")
    
    # 获取音色信息
    voice = db.query(PresetVoice).filter(PresetVoice.voice_id == request.voice_id).first()
    if not voice:
        raise HTTPException(status_code=400, detail=f"无效的音色 ID: {request.voice_id}")
    
    # 计算相对路径
    vocals_path = str(Path(song.vocals_file).relative_to(DATA_DIR))
    
    # 创建任务记录
    task = CloneTask(
        task_uuid=str(uuid.uuid4()),
        song_id=request.song_id,
        voice_id=request.voice_id,
        voice_name=voice.name,
        pitch_shift=request.pitch_shift,
        f0_method=request.f0_method,
        status=TaskStatus.PROCESSING
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                f"{RVC_URL}/clone",
                json={
                    "song_id": request.song_id,
                    "vocals_path": vocals_path,
                    "voice_id": request.voice_id,
                    "pitch_shift": request.pitch_shift,
                    "f0_method": request.f0_method
                },
            )
            resp.raise_for_status()
            data = resp.json()
            
            # 更新任务状态
            if data.get("status") == "completed":
                task.status = TaskStatus.COMPLETED
                task.output_file = data.get("output_path")
                task.processing_time = data.get("processing_time")
                task.completed_at = datetime.utcnow()
                
                # 更新歌曲状态
                song.cloned_file = data.get("output_path")
                song.clone_task_id = task.task_uuid
                song.status = SongStatus.CLONED
                db.commit()
            elif data.get("status") == "failed":
                task.status = TaskStatus.FAILED
                task.error_message = data.get("error")
                db.commit()
            
            return CloneResponse(**data)
            
        except httpx.HTTPError as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            db.commit()
            raise HTTPException(status_code=503, detail=f"RVC 服务不可用：{str(e)}")


# ============== 任务管理 ==============
@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """获取克隆任务状态"""
    task = db.query(CloneTask).filter(CloneTask.task_uuid == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return TaskStatusResponse(**task.to_dict())


@app.get("/api/v1/songs/{song_id}/tasks", response_model=List[TaskStatusResponse])
async def get_song_tasks(song_id: int, db: Session = Depends(get_db)):
    """获取歌曲的所有克隆任务"""
    tasks = db.query(CloneTask).filter(CloneTask.song_id == song_id).order_by(CloneTask.created_at.desc()).all()
    return [TaskStatusResponse(**task.to_dict()) for task in tasks]


@app.get("/api/v1/cloned/{task_id}/download")
async def download_cloned(task_id: str, db: Session = Depends(get_db)):
    """下载克隆结果"""
    task = db.query(CloneTask).filter(CloneTask.task_uuid == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if not task.output_file or not os.path.exists(task.output_file):
        raise HTTPException(status_code=404, detail="克隆文件不存在")
    
    song = db.query(Song).filter(Song.id == task.song_id).first()
    filename = f"{song.title}_{task.voice_name}_cloned.wav" if song else f"cloned_{task_id}.wav"
    
    return FileResponse(
        task.output_file,
        media_type="audio/wav",
        filename=filename
    )


# ============== 主程序 ==============
if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("MelodyClaw API 主服务")
    print(f"数据目录：{DATA_DIR}")
    print(f"Demucs: {DEMUCS_URL}")
    print(f"Silero: {SILERO_URL}")
    print(f"RVC: {RVC_URL}")
    print("端口：8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
