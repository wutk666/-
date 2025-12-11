from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    conn = db.engine.connect()
    try:
        # 获取 banned_ip 列信息
        res = conn.execute(text("PRAGMA table_info('banned_ip')")).fetchall()
        cols = [r[1] for r in res]
        changed = False

        if 'expires_at' not in cols:
            print("添加列: expires_at")
            conn.execute(text("ALTER TABLE banned_ip ADD COLUMN expires_at DATETIME"))
            changed = True

        if 'permanent' not in cols:
            print("添加列: permanent")
            # 默认 0（False）
            conn.execute(text("ALTER TABLE banned_ip ADD COLUMN permanent BOOLEAN DEFAULT 0"))
            changed = True

        if changed:
            print("迁移完成。")
        else:
            print("无需迁移：列已存在。")
    finally:
        conn.close()