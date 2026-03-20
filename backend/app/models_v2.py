"""MelodyClaw V2 数据库模型 - 互动式卡拉 OK 系统"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class RecordingV2(Base):
    """录制作品表 - V2 核心表"""
    __tablename__ = "recordings_v2"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(64), unique=True, nullable=False, index=True)
    song_id = Column(Integer, nullable=False)
    
    # 文件路径
    video_file = Column(String(512), nullable=False)
    thumbnail_file = Column(String(512), nullable=True)
    
    # 元数据
    duration = Column(Float, nullable=True)  # 视频时长（秒）
    
    # 位置信息（小龙虾和歌词的拖动位置）
    lobster_position = Column(JSON, nullable=True)  # {x: number, y: number}
    lyrics_position = Column(JSON, nullable=True)   # {x: number, y: number}
    
    # 统计
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "song_id": self.song_id,
            "video_file": self.video_file,
            "thumbnail_file": self.thumbnail_file,
            "duration": self.duration,
            "lobster_position": self.lobster_position,
            "lyrics_position": self.lyrics_position,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
