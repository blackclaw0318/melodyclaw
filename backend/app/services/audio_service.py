"""
音频服务层
处理歌曲上传、人声分离、获取和删除等核心业务逻辑
"""
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models import Song, SongStatus
from app.config import settings


class AudioService:
    """
    音频服务类
    封装所有音频相关的业务操作
    """

    def __init__(self, db: Session):
        """
        初始化音频服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        # 确保上传目录存在
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload_song(
        self,
        file: UploadFile,
        title: str,
        artist: Optional[str] = None
    ) -> Song:
        """
        上传歌曲文件
        
        Args:
            file: 上传的音频文件
            title: 歌曲标题
            artist: 艺术家 (可选)
            
        Returns:
            Song: 创建的歌曲记录
            
        Raises:
            ValueError: 文件保存失败时抛出
        """
        # 生成唯一文件名
        file_extension = Path(file.filename).suffix.lower() if file.filename else ".mp3"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        # 保存文件
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise ValueError(f"文件保存失败：{str(e)}")
        
        # 获取文件大小
        file_size = file_path.stat().st_size
        
        # 创建数据库记录
        song = Song(
            title=title,
            artist=artist,
            file_path=str(file_path),
            status=SongStatus.PENDING,
            file_size=file_size
        )
        
        self.db.add(song)
        self.db.commit()
        self.db.refresh(song)
        
        return song

    def separate_vocals(self, song_id: int, model_preset: str = "htdemucs") -> Song:
        """
        人声分离 (同步版本，实际使用异步任务)
        
        Args:
            song_id: 歌曲 ID
            model_preset: 分离模型预设
            
        Returns:
            Song: 更新后的歌曲记录
            
        Raises:
            ValueError: 歌曲不存在时抛出
        """
        song = self.db.query(Song).filter(Song.id == song_id).first()
        
        if not song:
            raise ValueError(f"歌曲不存在：{song_id}")
        
        # 更新状态为处理中
        song.status = SongStatus.PROCESSING
        self.db.commit()
        
        # TODO: 实际的人声分离逻辑
        # 这里将调用 AI 模型进行人声分离
        # 分离完成后更新状态和结果路径
        
        return song

    def get_song(self, song_id: int) -> Optional[Song]:
        """
        获取歌曲详情
        
        Args:
            song_id: 歌曲 ID
            
        Returns:
            Song: 歌曲记录，不存在则返回 None
        """
        return self.db.query(Song).filter(Song.id == song_id).first()

    def delete_song(self, song_id: int) -> bool:
        """
        删除歌曲及其相关文件
        
        Args:
            song_id: 歌曲 ID
            
        Returns:
            bool: 删除成功返回 True
            
        Raises:
            ValueError: 歌曲不存在时抛出
        """
        song = self.db.query(Song).filter(Song.id == song_id).first()
        
        if not song:
            raise ValueError(f"歌曲不存在：{song_id}")
        
        # 删除文件
        try:
            file_path = Path(song.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            # 文件删除失败，记录日志但不阻止数据库删除
            print(f"警告：文件删除失败 {song.file_path}: {str(e)}")
        
        # 删除数据库记录 (级联删除关联的 lyrics 和 clone_tasks)
        self.db.delete(song)
        self.db.commit()
        
        return True

    def get_all_songs(
        self,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[SongStatus] = None
    ) -> tuple[list[Song], int]:
        """
        获取歌曲列表
        
        Args:
            skip: 跳过数量
            limit: 返回数量
            status_filter: 状态筛选
            
        Returns:
            tuple: (歌曲列表，总数)
        """
        query = self.db.query(Song)
        
        if status_filter:
            query = query.filter(Song.status == status_filter)
        
        total = query.count()
        songs = query.offset(skip).limit(limit).all()
        
        return songs, total
