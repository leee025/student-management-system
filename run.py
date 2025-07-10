#!/usr/bin/env python
"""
Flask應用啟動文件
用於開發環境下啟動Flask應用服務器
"""

from app import create_app
# from flask_migrate import Migrate

# 創建Flask應用實例
app = create_app()

# 初始化數據庫遷移（目前已註釋，如需要可取消註釋）
# from app import db
# migrate = Migrate(app, db)

if __name__ == '__main__':
    """
    直接運行此文件時啟動Flask開發服務器
    注意：此配置僅適用於開發環境，生產環境請使用WSGI服務器
    """
    app.run(
        debug=True,        # 開啟調試模式，代碼修改後自動重載
        host='0.0.0.0',    # 監聽所有網絡接口，允許外部訪問
        port=5000          # 監聽端口號
    )