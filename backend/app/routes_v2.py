# -*- coding: utf-8 -*-
"""MelodyClaw V2 API - 录制作品相关端点"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import json
import shutil
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from database import get_db
from models_v2 import RecordingV2
from models import Song

# 视频处理服务
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.video_processor import VideoProcessor, process_upload

router = APIRouter(prefix="/api/v2", tags=["v2"])

# 数据目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RECORDINGS_DIR = DATA_DIR / "recordings"

# 确保目录存在
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/recordings")
async def create_recording(
    song_id: int = Form(...),
    video: UploadFile = File(...),
    lobster_position: Optional[str] = Form(None),
    lyrics_position: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """上传录制作品（支持后台转码）"""
    
    # 生成唯一 ID
    recording_uuid = str(uuid.uuid4())
    
    # 保存原始视频文件
    ext = Path(video.filename).suffix.lower() if video.filename else '.webm'
    if ext not in ['.webm', '.mp4', '.mov', '.mkv']:
        ext = '.webm'
    
    # 先保存原始文件
    original_filename = f"{recording_uuid}_original{ext}"
    original_path = RECORDINGS_DIR / original_filename
    
    with open(original_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    
    # 解析位置信息
    lobster_pos = json.loads(lobster_position) if lobster_position else None
    lyrics_pos = json.loads(lyrics_position) if lyrics_position else None
    
    # 如果是 WebM，后台转码为 MP4
    if ext == '.webm' and background_tasks:
        # 先创建记录（状态为 processing）
        video_filename = original_filename
        background_tasks.add_task(
            process_video_background,
            str(original_path),
            recording_uuid,
            song_id,
            lobster_pos,
            lyrics_pos,
            db
        )
        
        return {
            "id": None,  # 稍后更新
            "uuid": recording_uuid,
            "song_id": song_id,
            "status": "processing",
            "message": "视频正在处理中"
        }
    else:
        # 直接处理
        result = process_upload(str(original_path), str(RECORDINGS_DIR))
        
        # 获取视频时长
        duration = None
        try:
            processor = VideoProcessor()
            info = processor.get_video_info(result['video'])
            duration = float(info['format']['duration'])
        except Exception as e:
            print(f"获取视频时长失败：{e}")
        
        # 创建数据库记录
        recording = RecordingV2(
            uuid=recording_uuid,
            song_id=song_id,
            video_file=result['video'],
            thumbnail_file=result['thumbnail'],
            duration=duration,
            lobster_position=lobster_pos,
            lyrics_position=lyrics_pos
        )
        
        db.add(recording)
        
        # 更新歌曲合唱次数
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            song.duet_count = (song.duet_count or 0) + 1
        
        db.commit()
        db.refresh(recording)
        
        return {
            "id": recording.id,
            "uuid": recording.uuid,
            "song_id": song_id,
            "created_at": recording.created_at.isoformat()
        }


def process_video_background(
    original_path: str,
    recording_uuid: str,
    song_id: int,
    lobster_pos: dict,
    lyrics_pos: dict,
    db: Session
):
    """后台处理视频（转码 + 生成缩略图）"""
    try:
        result = process_upload(original_path, str(RECORDINGS_DIR))
        
        # 获取视频时长
        processor = VideoProcessor()
        info = processor.get_video_info(result['video'])
        duration = float(info['format']['duration'])
        
        # 创建数据库记录
        recording = RecordingV2(
            uuid=recording_uuid,
            song_id=song_id,
            video_file=result['video'],
            thumbnail_file=result['thumbnail'],
            duration=duration,
            lobster_position=lobster_pos,
            lyrics_position=lyrics_pos
        )
        
        db.add(recording)
        
        # 更新歌曲合唱次数
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            song.duet_count = (song.duet_count or 0) + 1
        
        db.commit()
        
        # 删除原始文件
        os.remove(original_path)
        
        print(f"视频处理完成：{recording_uuid}")
    except Exception as e:
        print(f"视频处理失败：{e}")
        db.rollback()


@router.get("/recordings")
async def list_recordings(
    page: int = 1,
    page_size: int = 20,
    song_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取作品列表"""
    
    query = db.query(RecordingV2)
    
    if song_id:
        query = query.filter(RecordingV2.song_id == song_id)
    
    total = query.count()
    recordings = query.order_by(RecordingV2.created_at.desc())\
                      .offset((page - 1) * page_size)\
                      .limit(page_size)\
                      .all()
    
    return {
        "recordings": [r.to_dict() for r in recordings],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/recordings/{recording_id}")
async def get_recording(recording_id: int, db: Session = Depends(get_db)):
    """获取作品详情"""
    
    recording = db.query(RecordingV2).filter(RecordingV2.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # 增加播放次数
    recording.view_count = (recording.view_count or 0) + 1
    db.commit()
    
    return recording.to_dict()


@router.get("/recordings/{recording_id}/video")
async def download_recording_video(recording_id: int, db: Session = Depends(get_db)):
    """下载作品视频"""
    
    recording = db.query(RecordingV2).filter(RecordingV2.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    if not recording.video_file or not os.path.exists(recording.video_file):
        raise HTTPException(status_code=404, detail="视频文件不存在")
    
    return FileResponse(
        recording.video_file,
        media_type="video/webm",
        filename=f"recording_{recording.uuid}.webm"
    )


@router.delete("/recordings/{recording_id}")
async def delete_recording(recording_id: int, db: Session = Depends(get_db)):
    """删除作品"""
    
    recording = db.query(RecordingV2).filter(RecordingV2.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # 删除文件
    try:
        if recording.video_file and os.path.exists(recording.video_file):
            os.remove(recording.video_file)
        if recording.thumbnail_file and os.path.exists(recording.thumbnail_file):
            os.remove(recording.thumbnail_file)
    except Exception as e:
        print(f"删除文件失败：{e}")
    
    # 删除数据库记录
    db.delete(recording)
    db.commit()
    
    return {"status": "deleted", "id": recording_id}


@router.post("/recordings/{recording_id}/like")
async def like_recording(recording_id: int, db: Session = Depends(get_db)):
    """点赞作品"""
    
    recording = db.query(RecordingV2).filter(RecordingV2.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    recording.like_count = (recording.like_count or 0) + 1
    db.commit()
    
    return {"likes": recording.like_count}


@router.post("/recordings/{recording_id}/view")
async def increment_view(recording_id: int, db: Session = Depends(get_db)):
    """增加播放次数"""
    
    recording = db.query(RecordingV2).filter(RecordingV2.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    recording.view_count = (recording.view_count or 0) + 1
    db.commit()
    
    return {"views": recording.view_count}
