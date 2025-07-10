"""
Flask應用管理腳本
提供數據庫初始化、用戶創建等管理命令
使用方法：python manage.py <command>
"""

from flask.cli import FlaskGroup
from flask_migrate import Migrate
from app import create_app, db
from datetime import datetime, timezone

# 創建Flask應用實例
app = create_app()

# 初始化數據庫遷移
migrate = Migrate(app, db)

# 創建Flask命令行組，用於執行自定義命令
cli = FlaskGroup(app)

@cli.command("init_db")
def init_db():
    """
    初始化數據庫命令
    創建所有數據表結構
    使用方法：python manage.py init_db
    """
    db.create_all()
    print('Database initialized!')

@cli.command("create_admin")
def create_admin():
    """
    創建管理員用戶命令
    創建一個默認的管理員賬戶（用戶名：admin，密碼：admin123）
    使用方法：python manage.py create_admin
    """
    from app.models import User

    # 創建管理員用戶對象
    admin = User(
        username='admin',           # 用戶名
        role='admin',              # 角色：管理員
        is_active=True,            # 賬戶狀態：啟用
        last_login=datetime.now(timezone.utc),  # 最後登錄時間
    )

    # 設置密碼（會自動進行哈希加密）
    admin.set_password('admin123')

    # 添加到數據庫會話
    db.session.add(admin)

    try:
        # 提交事務
        db.session.commit()
        print('Admin user created successfully!')
    except Exception as e:
        # 如果出錯則回滾事務
        db.session.rollback()
        print(f'Error creating admin user: {str(e)}')

if __name__ == '__main__':
    # 執行命令行界面
    cli()