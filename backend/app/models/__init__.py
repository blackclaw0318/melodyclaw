"""
数据模型定义
包含 Song、Lyrics、CloneTask 三个核心模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class SongStatus(str, enum.Enum):
    """歌曲状态枚举"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败


class CloneTaskStatus(str, enum.Enum):
    """克隆任务状态枚举"""
    PENDING = "pending"      # 待处理
    QUEUED = "queued"        # 已排队
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败


class Song(Base):
    """
    歌曲模型
    存储上传的原始歌曲信息
    """
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)  # 歌曲标题
    artist = Column(String(255), nullable=True)  # 艺术家
    file_path = Column(String(512), nullable=False)  # 文件路径
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)  # 上传日期
    status = Column(SQLEnum(SongStatus), default=SongStatus.PENDING, nullable=False)  # 状态
    duration = Column(Integer, nullable=True)  # 时长 (秒)
    file_size = Column(Integer, nullable=True)  # 文件大小 (字节)

    # 关联关系
    lyrics = relationship("Lyrics", back_populates="song", uselist=False, cascade="all, delete-orphan")
    clone_tasks = relationship("CloneTask", back_populates="song", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Song(id={self.id}, title='{self.title}', status='{self.status}')>"


class Lyrics(Base):
    """
    歌词模型
    存储歌曲的歌词内容，支持时间轴对齐
    """
    __tablename__ = "lyrics"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False, unique=True)  # 关联歌曲 ID
    content = Column(String, nullable=False)  # 歌词内容
    aligned = Column(Boolean, default=False, nullable=False)  # 是否已时间轴对齐
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # 关联关系
    song = relationship("Song", back_populates="lyrics")

    def __repr__(self):
        return f"<Lyrics(id={self.id}, song_id={self.song_id}, aligned={self.aligned})>"


class CloneTask(Base):
    """
    克隆任务模型
    存储 AI 歌声克隆任务信息
    """
    __tablename__ = "clone_tasks"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)  # 关联歌曲 ID
    voice_preset = Column(String(255), nullable=False)  # 声音预设 ID
    status = Column(SQLEnum(CloneTaskStatus), default=CloneTaskStatus.PENDING, nullable=False)  # 任务状态
    result_path = Column(String(512), nullable=True)  # 结果文件路径
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # 创建时间
    started_at = Column(DateTime, nullable=True)  # 开始时间
    completed_at = Column(DateTime, nullable=True)  # 完成时间
    error_message = Column(String(1024), nullable=True)  # 错误信息

    # 关联关系
    song = relationship("Song", back_populates="clone_tasks")

    def __repr__(self):
        return f"<CloneTask(id={self.id}, song_id={self.song_id}, status='{self.status}')>"
