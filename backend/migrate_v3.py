# -*- coding: utf-8 -*-
"""数据库迁移脚本 V2 -> V3（用户系统）"""

import sqlite3
import sys
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "app" / "melodyclaw.db"

def migrate():
    print("开始数据库迁移 V2 -> V3（用户系统）...")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # 1. 创建 users 表
        print("  [1/6] 创建 users 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(64) UNIQUE NOT NULL,
                email VARCHAR(128) UNIQUE,
                password_hash VARCHAR(256) NOT NULL,
                avatar_url VARCHAR(512),
                nickname VARCHAR(64),
                bio TEXT,
                phone VARCHAR(20),
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                is_vip BOOLEAN DEFAULT 0,
                vip_expire_at DATETIME,
                following_count INTEGER DEFAULT 0,
                follower_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                work_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login_at DATETIME
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        print("    + users 表已创建")
        
        # 2. 创建 user_follows 表
        print("  [2/6] 创建 user_follows 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_follows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower_id INTEGER NOT NULL,
                following_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users(id),
                FOREIGN KEY (following_id) REFERENCES users(id),
                UNIQUE(follower_id, following_id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_follows_follower ON user_follows(follower_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_follows_following ON user_follows(following_id)")
        print("    + user_follows 表已创建")
        
        # 3. 创建 user_favorites 表
        print("  [3/6] 创建 user_favorites 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recording_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_user ON user_favorites(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_recording ON user_favorites(recording_id)")
        print("    + user_favorites 表已创建")
        
        # 4. 创建 comments 表
        print("  [4/6] 创建 comments 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recording_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                parent_id INTEGER,
                like_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_recording ON comments(recording_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_user ON comments(user_id)")
        print("    + comments 表已创建")
        
        # 5. 创建 vip_packages 表
        print("  [5/6] 创建 vip_packages 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vip_packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(128) NOT NULL,
                description TEXT,
                price FLOAT NOT NULL,
                original_price FLOAT,
                duration_days INTEGER NOT NULL,
                features TEXT,
                is_active BOOLEAN DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("    + vip_packages 表已创建")
        
        # 6. 创建 vip_voices 表
        print("  [6/6] 创建 vip_voices 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vip_voices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voice_id VARCHAR(64) UNIQUE NOT NULL,
                name VARCHAR(128) NOT NULL,
                description VARCHAR(256),
                f0_min INTEGER DEFAULT 80,
                f0_max INTEGER DEFAULT 400,
                model_path VARCHAR(512),
                preview_url VARCHAR(512),
                is_active BOOLEAN DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("    + vip_voices 表已创建")
        
        # 插入默认 VIP 套餐
        print("  插入默认 VIP 套餐...")
        default_packages = [
            ("月度会员", "30 天 VIP 会员，享受所有 VIP 音色", 19.9, 29.9, 30, '["所有 VIP 音色", "高清导出", "无限云存储"]'),
            ("季度会员", "90 天 VIP 会员，超值优惠", 49.9, 89.7, 90, '["所有 VIP 音色", "高清导出", "无限云存储", "优先客服"]'),
            ("年度会员", "365 天 VIP 会员，最划算", 168.0, 358.8, 365, '["所有 VIP 音色", "4K 导出", "无限云存储", "专属客服", "抢先体验新功能"]')
        ]
        
        for pkg in default_packages:
            cursor.execute("""
                INSERT OR IGNORE INTO vip_packages (name, description, price, original_price, duration_days, features)
                VALUES (?, ?, ?, ?, ?, ?)
            """, pkg)
        
        # 插入默认 VIP 音色
        print("  插入默认 VIP 音色...")
        default_voices = [
            ("vip_pop_star", "流行明星", "热门流行歌手音色", 100, 500),
            ("vip_rock_legend", "摇滚传奇", "经典摇滚歌手音色", 80, 450),
            ("vip_jazz_diva", "爵士歌后", "爵士女伶音色", 150, 600),
            ("vip_electronic", "电子合成", "未来感电子音色", 90, 480)
        ]
        
        for voice in default_voices:
            cursor.execute("""
                INSERT OR IGNORE INTO vip_voices (voice_id, name, description, f0_min, f0_max)
                VALUES (?, ?, ?, ?, ?)
            """, voice)
        
        conn.commit()
        print("\n迁移完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"\n迁移失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
