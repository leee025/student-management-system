"""
用戶認證藍圖初始化
處理用戶登錄、註冊、登出等認證相關功能
"""

from flask import Blueprint

# 創建認證藍圖
bp = Blueprint('auth', __name__)

# 導入路由模塊（必須在藍圖創建後導入以避免循環導入）
from app.auth import routes