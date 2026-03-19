"""数据库配置"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库路径
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./melodyclaw.db")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 需要
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库 (创建表)"""
    from models import Base
    Base.metadata.create_all(bind=engine)
    
    # 插入预设音色
    from models import PresetVoice
    db = SessionLocal()
    try:
        preset_voices = [
            {"voice_id": "pop_male", "name": "流行男声", "style": "温暖明亮", "f0_min": 80, "f0_max": 400},
            {"voice_id": "pop_female", "name": "流行女声", "style": "清澈甜美", "f0_min": 150, "f0_max": 600},
            {"voice_id": "rock_male", "name": "摇滚男声", "style": "粗犷有力", "f0_min": 70, "f0_max": 350},
            {"voice_id": "ballad", "name": "民谣嗓音", "style": "朴实自然", "f0_min": 90, "f0_max": 420},
            {"voice_id": "child", "name": "童声", "style": "稚嫩可爱", "f0_min": 200, "f0_max": 800},
            {"voice_id": "deep", "name": "低沉嗓音", "style": "浑厚磁性", "f0_min": 60, "f0_max": 300},
        ]
        
        for voice_data in preset_voices:
            existing = db.query(PresetVoice).filter(PresetVoice.voice_id == voice_data["voice_id"]).first()
            if not existing:
                voice = PresetVoice(**voice_data)
                db.add(voice)
        
        db.commit()
        print(f"[✓] 数据库初始化完成，预设音色：{len(preset_voices)} 种")
    finally:
        db.close()
