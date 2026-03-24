"""
歌曲 API 路由
提供歌曲的 CRUD 操作和人声分离功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.audio_service import AudioService
from app.tasks.audio_tasks import separate_vocals_task
from app.models import Song, SongStatus
from app.config import get_db

router = APIRouter()


# ==================== Pydantic 模型 ====================

class SongBase(BaseModel):
    """歌曲基础模型"""
    title: str = Field(..., min_length=1, max_length=255, description="歌曲标题")
    artist: Optional[str] = Field(None, max_length=255, description="艺术家")


class SongCreate(SongBase):
    """创建歌曲请求模型"""
    pass


class SongResponse(SongBase):
    """歌曲响应模型"""
    id: int
    file_path: str
    upload_date: datetime
    status: str
    duration: Optional[int] = None
    file_size: Optional[int] = None

    class Config:
        from_attributes = True


class SongListResponse(BaseModel):
    """歌曲列表响应模型"""
    total: int
    songs: List[SongResponse]


class SeparateVocalsRequest(BaseModel):
    """人声分离请求模型"""
    model_preset: str = Field(default="htdemucs", description="分离模型预设")


class SeparateVocalsResponse(BaseModel):
    """人声分离响应模型"""
    task_id: int
    status: str
    message: str


# ==================== API 路由 ====================

@router.get("/songs", response_model=SongListResponse, summary="获取歌曲列表")
async def get_songs(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取歌曲列表
    
    - **skip**: 跳过数量 (分页)
    - **limit**: 返回数量 (分页)
    - **status_filter**: 按状态筛选 (pending/processing/completed/failed)
    """
    query = db.query(Song)
    
    # 状态筛选
    if status_filter:
        try:
            status_enum = SongStatus(status_filter)
            query = query.filter(Song.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值：{status_filter}"
            )
    
    total = query.count()
    songs = query.offset(skip).limit(limit).all()
    
    return SongListResponse(total=total, songs=songs)


@router.post("/songs", response_model=SongResponse, status_code=status.HTTP_201_CREATED, summary="上传歌曲")
async def upload_song(
    file: UploadFile = File(..., description="音频文件"),
    title: str = Field(..., min_length=1, description="歌曲标题"),
    artist: Optional[str] = Field(None, description="艺术家"),
    db: Session = Depends(get_db)
):
    """
    上传歌曲文件
    
    - **file**: 音频文件 (支持 mp3, wav, flac 等格式)
    - **title**: 歌曲标题
    - **artist**: 艺术家 (可选)
    """
    # 验证文件类型
    allowed_types = ["audio/mpeg", "audio/wav", "audio/flac", "audio/mp3", "audio/x-wav"]
    if file.content_type not in allowed_types and not file.filename.lower().endswith(('.mp3', '.wav', '.flac')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件格式，请上传 mp3, wav 或 flac 文件"
        )
    
    # 使用音频服务上传
    audio_service = AudioService(db)
    try:
        song = audio_service.upload_song(
            file=file,
            title=title,
            artist=artist
        )
        return song
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败：{str(e)}"
        )


@router.get("/songs/{song_id}", response_model=SongResponse, summary="获取歌曲详情")
async def get_song(song_id: int, db: Session = Depends(get_db)):
    """
    获取歌曲详细信息
    
    - **song_id**: 歌曲 ID
    """
    audio_service = AudioService(db)
    song = audio_service.get_song(song_id)
    
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"歌曲不存在：{song_id}"
        )
    
    return song


@router.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除歌曲")
async def delete_song(song_id: int, db: Session = Depends(get_db)):
    """
    删除歌曲及其相关文件
    
    - **song_id**: 歌曲 ID
    """
    audio_service = AudioService(db)
    
    try:
        audio_service.delete_song(song_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败：{str(e)}"
        )


@router.post("/songs/{song_id}/separate", response_model=SeparateVocalsResponse, summary="人声分离")
async def separate_vocals(
    song_id: int,
    request: SeparateVocalsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    启动人声分离任务
    
    使用 AI 模型将歌曲分离为人声和伴奏
    
    - **song_id**: 歌曲 ID
    - **model_preset**: 分离模型预设 (默认：htdemucs)
    """
    audio_service = AudioService(db)
    
    # 验证歌曲存在
    song = audio_service.get_song(song_id)
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"歌曲不存在：{song_id}"
        )
    
    # 创建 Celery 异步任务
    try:
        task = separate_vocals_task.delay(song_id=song_id, model_preset=request.model_preset)
        
        return SeparateVocalsResponse(
            task_id=task.id if hasattr(task, 'id') else song_id,
            status="queued",
            message="人声分离任务已加入队列"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务创建失败：{str(e)}"
        )
