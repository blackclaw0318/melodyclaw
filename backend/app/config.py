"""
MelodyClaw 配置管理
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "MelodyClaw"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 项目路径
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    BACKEND_DIR: Path = Path(__file__).parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    AI_MODELS_DIR: Path = BASE_DIR / "ai_models"
    
    # 存储路径
    UPLOADS_DIR: Path = STORAGE_DIR / "uploads"
    PROCESSED_DIR: Path = STORAGE_DIR / "processed"
    CACHE_DIR: Path = STORAGE_DIR / "cache"
    
    # 模型配置
    DEMUCS_MODEL: str = "htdemucs_ft"
    SILERO_MODEL: str = "silero_vad"
    RVC_MODEL_DIR: Path = AI_MODELS_DIR / "rvc"
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_RESULT_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./melodyclaw.db"
    
    # 内存限制 (MB)
    MAX_MEMORY_MB: int = 14000  # 16GB 系统保留 2GB
    
    # 音频配置
    DEFAULT_SAMPLE_RATE: int = 44100
    DEFAULT_FORMAT: str = "wav"
    
    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def ensure_dirs(self):
        """确保所有目录存在"""
        for dir_path in [self.STORAGE_DIR, self.UPLOADS_DIR, self.PROCESSED_DIR, 
                         self.CACHE_DIR, self.AI_MODELS_DIR, self.RVC_MODEL_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
settings.ensure_dirs()


# 数据库依赖
def get_db():
    """获取数据库会话（占位实现，实际使用 SQLAlchemy）"""
    # TODO: 实现实际的数据库会话管理
    pass
