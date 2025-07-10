"""
學生管理藍圖初始化
處理學生相關的CRUD操作和管理功能
"""

from flask import Blueprint

# 創建學生管理藍圖，設置URL前綴
bp = Blueprint('student_management', __name__, url_prefix='/students')

# 導入路由模塊（必須在藍圖創建後導入以避免循環導入）
from app.student import routes