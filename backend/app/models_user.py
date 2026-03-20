# -*- coding: utf-8 -*-
"""MelodyClaw 用户系统数据库模型"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=True, index=True)
    password_hash = Column(String(256), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    
    # 用户信息
    nickname = Column(String(64), nullable=True)
    bio = Column(Text, nullable=True)  # 个人简介
    phone = Column(String(20), nullable=True)
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # 邮箱验证
    is_vip = Column(Boolean, default=False)  # VIP 会员
    vip_expire_at = Column(DateTime, nullable=True)
    
    # 统计信息
    following_count = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)  # 收到的赞
    work_count = Column(Integer, default=0)  # 作品数量
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "is_vip": self.is_vip,
            "follower_count": self.follower_count,
            "following_count": self.following_count,
            "like_count": self.like_count,
            "work_count": self.work_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserFollow(Base):
    """关注关系表"""
    __tablename__ = "user_follows"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关注者
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 被关注者
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 唯一约束：不能重复关注
    __table_args__ = (
        # 这里省略具体的 unique constraint 定义，实际使用需要添加
    )


class UserFavorite(Base):
    """用户收藏表"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recording_id = Column(Integer, nullable=False)  # 作品 ID
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recording_id = Column(Integer, nullable=False)  # 作品 ID
    
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, nullable=True)  # 回复评论的 ID
    
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recording_id": self.recording_id,
            "content": self.content,
            "parent_id": self.parent_id,
            "like_count": self.like_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class VipPackage(Base):
    """VIP 套餐表"""
    __tablename__ = "vip_packages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)  # 套餐名称
    description = Column(Text, nullable=True)
    
    # 价格
    price = Column(Float, nullable=False)  # 价格（元）
    original_price = Column(Float, nullable=True)  # 原价
    
    # 时长
    duration_days = Column(Integer, nullable=False)  # 有效期（天）
    
    # 权益
    features = Column(Text, nullable=True)  # JSON 格式存储权益列表
    
    # 状态
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "original_price": self.original_price,
            "duration_days": self.duration_days,
            "features": self.features,
            "is_active": self.is_active,
        }


class VipVoice(Base):
    """VIP 音色表"""
    __tablename__ = "vip_voices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    voice_id = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=True)
    
    # 音色参数
    f0_min = Column(Integer, default=80)
    f0_max = Column(Integer, default=400)
    model_path = Column(String(512), nullable=True)
    
    # 预览
    preview_url = Column(String(512), nullable=True)
    
    # 状态
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.voice_id,
            "name": self.name,
            "description": self.description,
            "f0_min": self.f0_min,
            "f0_max": self.f0_max,
            "preview_url": self.preview_url,
            "is_active": self.is_active,
        }
