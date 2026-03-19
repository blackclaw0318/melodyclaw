"""MelodyClaw 数据库模型"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class SongStatus(str, enum.Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    SEPARATED = "separated"
    ALIGNED = "aligned"
    CLONED = "cloned"
    FAILED = "failed"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Song(Base):
    """歌曲表"""
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=True)
    original_file = Column(String(512), nullable=False)  # 原始音频文件路径
    duration = Column(Float, nullable=True)  # 时长 (秒)
    sample_rate = Column(Integer, default=44100)
    status = Column(Enum(SongStatus), default=SongStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联文件
    vocals_file = Column(String(512), nullable=True)  # 人声文件
    accompaniment_file = Column(String(512), nullable=True)  # 伴奏文件
    aligned_lyrics = Column(Text, nullable=True)  # 对齐后的歌词 (JSON)
    cloned_file = Column(String(512), nullable=True)  # 克隆结果
    
    # 关联任务
    separate_task_id = Column(String(64), nullable=True)
    align_task_id = Column(String(64), nullable=True)
    clone_task_id = Column(String(64), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "has_vocals": self.vocals_file is not None,
            "has_accompaniment": self.accompaniment_file is not None,
            "has_aligned_lyrics": self.aligned_lyrics is not None,
            "has_cloned": self.cloned_file is not None,
        }


class CloneTask(Base):
    """克隆任务表"""
    __tablename__ = "clone_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_uuid = Column(String(64), unique=True, nullable=False, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    voice_id = Column(String(64), nullable=False)  # 音色 ID
    voice_name = Column(String(128), nullable=True)  # 音色名称
    pitch_shift = Column(Integer, default=0)  # 音调偏移 (半音)
    f0_method = Column(String(32), default="dio")  # F0 提取方法
    
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    progress = Column(Integer, default=0)  # 进度 0-100
    error_message = Column(Text, nullable=True)
    
    output_file = Column(String(512), nullable=True)  # 输出文件路径
    processing_time = Column(Float, nullable=True)  # 处理时间 (秒)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # 关联歌曲
    song = relationship("Song", backref="clone_tasks")
    
    def to_dict(self):
        return {
            "id": self.id,
            "task_uuid": self.task_uuid,
            "song_id": self.song_id,
            "voice_id": self.voice_id,
            "voice_name": self.voice_name,
            "pitch_shift": self.pitch_shift,
            "status": self.status.value,
            "progress": self.progress,
            "error_message": self.error_message,
            "output_file": self.output_file,
            "processing_time": self.processing_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class PresetVoice(Base):
    """预设音色表"""
    __tablename__ = "preset_voices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    voice_id = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=True)
    style = Column(String(64), nullable=True)
    f0_min = Column(Integer, default=80)
    f0_max = Column(Integer, default=400)
    is_active = Column(Integer, default=1)  # 1=active, 0=inactive
    
    def to_dict(self):
        return {
            "id": self.voice_id,
            "name": self.name,
            "description": self.description,
            "style": self.style,
            "f0_min": self.f0_min,
            "f0_max": self.f0_max,
        }
