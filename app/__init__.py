"""
Flask應用工廠模式實現
包含應用創建、擴展初始化、藍圖註冊等核心功能
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# 初始化Flask擴展
# 注意：這裡只是創建擴展實例，實際初始化在create_app函數中進行

# SQLAlchemy數據庫ORM擴展
db = SQLAlchemy()

# Flask-Login用戶會話管理擴展
login_manager = LoginManager()
# 設置登錄視圖，未登錄用戶會被重定向到此路由
login_manager.login_view = 'auth.login'
# 設置未登錄時的提示消息
login_manager.login_message = '請先登錄以訪問此頁面'

def create_app(config_class=Config):
    """
    Flask應用工廠函數
    創建並配置Flask應用實例

    Args:
        config_class: 配置類，默認為Config

    Returns:
        Flask: 配置完成的Flask應用實例
    """
    import os

    # 設置模板文件夾路徑
    template_path = os.path.join(os.path.dirname(__file__), 'templates')

    # 創建Flask應用實例
    app = Flask(__name__, template_folder=template_path)

    # 從配置類載入配置
    app.config.from_object(config_class)

    # 初始化Flask擴展
    # 將擴展與應用實例綁定
    db.init_app(app)
    login_manager.init_app(app)

    # 設置登錄後的默認重定向路由
    app.config['LOGIN_REDIRECT_URL'] = 'index'

    # 添加模板全局函數
    @app.template_global()
    def now():
        """返回當前日期時間，供模板使用"""
        from datetime import datetime
        return datetime.now()

    # 添加自定義模板過濾器
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """將換行符轉換為 HTML <br> 標籤"""
        if not text:
            return text
        import re
        # 將 \n 和 \r\n 轉換為 <br>
        return re.sub(r'\r?\n', '<br>', str(text))

    # 註冊藍圖（Blueprint）
    # 藍圖是Flask中組織路由和視圖的方式，有助於模組化應用結構

    # 用戶認證藍圖（登錄、註冊、登出等功能）
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 學生管理藍圖（學生CRUD操作）
    from app.student import bp as student_management_bp
    app.register_blueprint(student_management_bp)

    # 教師管理藍圖（教師CRUD操作）
    from app.teacher import bp as teacher_management_bp
    app.register_blueprint(teacher_management_bp)

    # 班級管理藍圖（班級CRUD操作）
    from app.classes import bp as class_management_bp
    app.register_blueprint(class_management_bp)

    # 用戶管理藍圖（用戶賬戶管理）
    from app.user_management import bp as user_management_bp
    app.register_blueprint(user_management_bp)

    # 全局搜尋藍圖（跨模組搜尋功能）
    from app.search import bp as search_bp
    app.register_blueprint(search_bp)

    # 建立首頁路由
    @app.route('/')
    def index():
        """
        首頁視圖函數
        顯示系統儀表板，包含統計數據和最近活動

        Returns:
            str: 渲染後的HTML頁面
        """
        from app.models import Teacher, Student, Class, User, Department
        from datetime import datetime, timedelta

        # 收集基本統計數據
        # 統計各類實體的總數量
        stats = {
            'total_students': Student.query.count(),      # 學生總數
            'total_teachers': Teacher.query.count(),      # 教師總數
            'total_classes': Class.query.count(),         # 班級總數
            'total_users': User.query.count(),            # 用戶總數
            'total_departments': Department.query.count() # 部門總數
        }

        # 計算最近一週新增的學生數量
        week_ago = datetime.utcnow() - timedelta(days=7)
        stats['new_students_this_week'] = Student.query.filter(
            Student.created_at >= week_ago
        ).count()

        # 獲取最近登錄的用戶（最多5個）
        # 只顯示有登錄記錄的用戶，按最後登錄時間降序排列
        recent_users = User.query.filter(
            User.last_login.isnot(None)
        ).order_by(User.last_login.desc()).limit(5).all()

        # 渲染首頁模板，傳遞統計數據和最近用戶信息
        return render_template('index.html',
                             title='儀表板',
                             stats=stats,
                             recent_users=recent_users)

    # 返回配置完成的Flask應用實例
    return app