# -*- coding: utf-8 -*-
"""数据库迁移脚本 V1 -> V2

功能：
1. 扩展 songs 表（新增封面、BPM、伴奏文件、合唱次数）
2. 创建 recordings_v2 表（录制作品）
"""

import sqlite3
import sys
from pathlib import Path

# 数据库路径（backend/app 目录）
DB_PATH = Path(__file__).parent / "app" / "melodyclaw.db"

def migrate():
    print("开始数据库迁移 V1 -> V2...")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # 1. 扩展 songs 表
        print("  [1/3] 扩展 songs 表...")
        
        columns_to_add = [
            ("cover_file", "VARCHAR(512)"),
            ("bpm", "INTEGER"),
            ("accompaniment_file", "VARCHAR(512)"),
            ("duet_count", "INTEGER DEFAULT 0")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE songs ADD COLUMN {col_name} {col_type}")
                print(f"    + 添加列：{col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"    - 列已存在：{col_name}")
                else:
                    raise
        
        # 2. 创建 recordings_v2 表
        print("  [2/3] 创建 recordings_v2 表...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recordings_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid VARCHAR(64) UNIQUE NOT NULL,
                song_id INTEGER NOT NULL,
                video_file VARCHAR(512) NOT NULL,
                thumbnail_file VARCHAR(512),
                duration FLOAT,
                lobster_position JSON,
                lyrics_position JSON,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                share_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("    + recordings_v2 表已创建")
        
        # 3. 创建索引
        print("  [3/3] 创建索引...")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recordings_uuid ON recordings_v2(uuid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recordings_song_id ON recordings_v2(song_id)")
        print("    + 索引已创建")
        
        conn.commit()
        print("\n迁移完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"\n迁移失败：{e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
