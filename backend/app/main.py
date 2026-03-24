"""
FastAPI 主应用入口
MelodyClaw 后端服务启动点
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1 import songs as songs_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🎵 MelodyClaw 服务启动中...")
    yield
    # 关闭时执行
    print("🎵 MelodyClaw 服务关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="MelodyClaw API",
    description="AI 歌声克隆系统后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(songs_router.router, prefix="/api/v1", tags=["songs"])


@app.get("/health", tags=["health"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "MelodyClaw",
        "version": "1.0.0"
    }


@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "message": "欢迎使用 MelodyClaw API",
        "docs": "/docs",
        "health": "/health"
    }
