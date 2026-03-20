# -*- coding: utf-8 -*-
"""MelodyClaw 用户认证 API"""

from fastapi import APIRouter, HTTPException, Depends, status, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import jwt
import hashlib

import sys
sys.path.insert(0, str(Path(__file__).parent))
from database import get_db
from models_user import User, UserFollow, UserFavorite, Comment, VipPackage, VipVoice

router = APIRouter(prefix="/api/v3", tags=["user"])

# JWT 配置
SECRET_KEY = "melodyclaw_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v3/auth/login")


# ============== 数据模型 ==============
class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserProfile(BaseModel):
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


# ============== 工具函数 ==============
def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


# ============== 认证端点 ==============
@router.post("/auth/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        email=user_data.email,
        nickname=user_data.nickname or user_data.username,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 生成 Token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "message": "注册成功",
        "user_id": user.id,
        "username": user.username,
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="账户已被禁用")
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 生成 Token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.get("/auth/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user.to_dict()


@router.put("/profile", response_model=dict)
async def update_profile(
    profile: UserProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新个人资料"""
    
    if profile.nickname is not None:
        current_user.nickname = profile.nickname
    if profile.bio is not None:
        current_user.bio = profile.bio
    if profile.avatar_url is not None:
        current_user.avatar_url = profile.avatar_url
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "更新成功", "user": current_user.to_dict()}


# ============== 关注功能 ==============
@router.post("/users/{user_id}/follow")
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """关注用户"""
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能关注自己")
    
    # 检查是否已关注
    existing = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id
    ).first()
    
    if existing:
        # 取消关注
        db.delete(existing)
        message = "已取消关注"
    else:
        # 添加关注
        follow = UserFollow(follower_id=current_user.id, following_id=user_id)
        db.add(follow)
        message = "关注成功"
    
    # 更新计数
    follower = db.query(User).filter(User.id == user_id).first()
    follower.follower_count = db.query(UserFollow).filter(UserFollow.following_id == user_id).count()
    
    current_user.following_count = db.query(UserFollow).filter(UserFollow.follower_id == current_user.id).count()
    
    db.commit()
    
    return {"message": message, "follower_count": follower.follower_count}


# ============== 收藏功能 ==============
@router.post("/recordings/{recording_id}/favorite")
async def toggle_favorite(
    recording_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """收藏/取消收藏作品"""
    
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.recording_id == recording_id
    ).first()
    
    if existing:
        db.delete(existing)
        message = "已取消收藏"
        is_favorited = False
    else:
        favorite = UserFavorite(user_id=current_user.id, recording_id=recording_id)
        db.add(favorite)
        message = "收藏成功"
        is_favorited = True
    
    db.commit()
    
    return {"message": message, "is_favorited": is_favorited}


@router.get("/favorites")
async def get_favorites(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的收藏"""
    
    favorites = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id)\
                  .order_by(UserFavorite.created_at.desc())\
                  .offset((page - 1) * page_size)\
                  .limit(page_size)\
                  .all()
    
    total = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id).count()
    
    return {
        "favorites": [{"recording_id": f.recording_id, "created_at": f.created_at.isoformat()} for f in favorites],
        "total": total,
        "page": page
    }


# ============== 评论功能 ==============
@router.post("/recordings/{recording_id}/comments")
async def add_comment(
    recording_id: int,
    content: str = Form(...),
    parent_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发表评论"""
    
    comment = Comment(
        user_id=current_user.id,
        recording_id=recording_id,
        content=content,
        parent_id=parent_id
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {"message": "评论成功", "comment": comment.to_dict()}


@router.get("/recordings/{recording_id}/comments")
async def get_comments(
    recording_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取作品评论"""
    
    comments = db.query(Comment).filter(Comment.recording_id == recording_id, Comment.parent_id == None)\
               .order_by(Comment.created_at.desc())\
               .offset((page - 1) * page_size)\
               .limit(page_size)\
               .all()
    
    total = db.query(Comment).filter(Comment.recording_id == recording_id, Comment.parent_id == None).count()
    
    return {
        "comments": [c.to_dict() for c in comments],
        "total": total,
        "page": page
    }


# ============== VIP 功能 ==============
@router.get("/vip/packages")
async def get_vip_packages(db: Session = Depends(get_db)):
    """获取 VIP 套餐列表"""
    
    packages = db.query(VipPackage).filter(VipPackage.is_active == True)\
                .order_by(VipPackage.sort_order)\
                .all()
    
    return {"packages": [p.to_dict() for p in packages]}


@router.get("/vip/voices")
async def get_vip_voices(db: Session = Depends(get_db)):
    """获取 VIP 音色列表"""
    
    voices = db.query(VipVoice).filter(VipVoice.is_active == True)\
              .order_by(VipVoice.sort_order)\
              .all()
    
    return {"voices": [v.to_dict() for v in voices]}


@router.get("/vip/status")
async def get_vip_status(current_user: User = Depends(get_current_user)):
    """获取 VIP 状态"""
    
    is_vip = current_user.is_vip
    vip_expire_at = current_user.vip_expire_at.isoformat() if current_user.vip_expire_at else None
    
    return {
        "is_vip": is_vip,
        "vip_expire_at": vip_expire_at,
        "username": current_user.username
    }
