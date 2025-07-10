"""
Flask應用配置文件
包含數據庫連接、安全密鑰等重要配置信息
"""
import os
from dotenv import load_dotenv

# 獲取項目根目錄的絕對路徑
basedir = os.path.abspath(os.path.dirname(__file__))

# 載入環境變量文件(.env)
load_dotenv()

class Config:
    """
    Flask應用配置類
    包含所有應用運行所需的配置參數
    """

    # Flask核心配置
    # 用於會話加密和CSRF保護的密鑰，生產環境中必須設置為隨機字符串
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'

    # 數據庫配置
    # 從環境變量獲取數據庫連接URL，如果沒有則使用默認的本地MySQL配置
    # 格式：mysql+pymysql://用戶名:密碼@主機地址/數據庫名
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:@10.128.174.95/student'

    # 禁用SQLAlchemy的事件系統以節省資源
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 分頁配置
    # 每頁顯示的記錄數量，用於列表頁面的分頁功能
    ITEMS_PER_PAGE = 10