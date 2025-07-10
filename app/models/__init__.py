"""
數據模型定義
包含學生管理系統的所有數據表模型
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(id):
    """
    Flask-Login用戶載入回調函數
    根據用戶ID從數據庫載入用戶對象

    Args:
        id (str): 用戶ID

    Returns:
        User: 用戶對象，如果不存在則返回None
    """
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    """
    用戶模型
    存儲系統用戶的基本信息和認證數據
    繼承自UserMixin以支持Flask-Login功能
    """
    __tablename__ = 'users'

    # 主鍵：用戶ID
    user_id = db.Column(db.Integer, primary_key=True)

    # 用戶名：唯一，不能為空
    username = db.Column(db.String(50), unique=True, nullable=False)

    # 密碼哈希值：存儲加密後的密碼，不能為空
    password_hash = db.Column(db.String(255), nullable=False)

    # 用戶角色：管理員、教師、學生、職員，默認為學生
    role = db.Column(db.Enum('admin', 'teacher', 'student', 'staff'), nullable=False, default='student')

    # 關聯ID：用於關聯到具體的教師或學生記錄
    related_id = db.Column(db.String(20))

    # 賬戶狀態：是否啟用，默認為啟用
    is_active = db.Column(db.Boolean, default=True)

    # 最後登錄時間
    last_login = db.Column(db.TIMESTAMP)

    # 創建時間：使用數據庫默認值
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    # 更新時間：創建時使用默認值，更新時自動更新
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def get_id(self):
        """
        Flask-Login要求的方法
        返回用戶的唯一標識符

        Returns:
            str: 用戶ID的字符串形式
        """
        return str(self.user_id)

    def set_password(self, password):
        """
        設置用戶密碼
        將明文密碼進行哈希加密後存儲

        Args:
            password (str): 明文密碼
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        驗證用戶密碼
        將輸入的明文密碼與存儲的哈希值進行比較

        Args:
            password (str): 待驗證的明文密碼

        Returns:
            bool: 密碼是否正確
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """
        對象的字符串表示

        Returns:
            str: 用戶對象的描述
        """
        return f'<User {self.username}>'

class Student(db.Model):
    """
    學生模型
    存儲學生的基本信息和學籍數據
    """
    __tablename__ = 'students'

    # 主鍵：學生學號
    student_id = db.Column(db.String(20), primary_key=True)

    # 學生姓名：不能為空
    name = db.Column(db.String(100), nullable=False)

    # 班級ID：外鍵關聯到classes表
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'))

    # 性別：男或女，不能為空
    gender = db.Column(db.Enum('男', '女'), nullable=False)

    # 出生日期
    birth_date = db.Column(db.Date)

    # 住址
    address = db.Column(db.String(200))

    # 聯繫電話
    phone = db.Column(db.String(20))

    # 電子郵箱
    email = db.Column(db.String(100))

    # 入學日期
    enrollment_date = db.Column(db.Date)

    # 學籍狀態：在學、休學、退學、畢業
    status = db.Column(db.Enum('在學', '休學', '退學', '畢業'))

    # 身份證號碼
    id_number = db.Column(db.String(18))

    # 記錄創建時間
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    # 記錄更新時間
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯關係：學生所屬班級
    # backref='students' 在Class模型中創建反向關係
    class_info = db.relationship('Class', backref=db.backref('students', lazy=True))

    def __repr__(self):
        """
        對象的字符串表示

        Returns:
            str: 學生對象的描述
        """
        return f'<Student {self.name}>'

class Class(db.Model):
    """
    班級模型
    存儲班級的基本信息和關聯關係
    """
    __tablename__ = 'classes'

    # 主鍵：班級ID
    class_id = db.Column(db.Integer, primary_key=True)

    # 班級名稱：不能為空
    class_name = db.Column(db.String(100), nullable=False)

    # 年級：不能為空
    grade = db.Column(db.Integer, nullable=False)

    # 所屬部門ID：外鍵關聯到departments表
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))

    # 班主任教師ID：外鍵關聯到teachers表
    teacher_id = db.Column(db.String(20), db.ForeignKey('teachers.teacher_id'))

    # 關聯關係：班級所屬部門
    department = db.relationship('Department', backref='classes')

    # 關聯關係：班級的班主任教師
    # 使用primaryjoin指定關聯條件
    teacher = db.relationship('Teacher', backref='classes',
                            primaryjoin="Class.teacher_id == Teacher.teacher_id")

    def __repr__(self):
        """
        對象的字符串表示

        Returns:
            str: 班級對象的描述
        """
        return f'<Class {self.class_name}>'

class Department(db.Model):
    """
    部門模型
    存儲學校部門的基本信息
    """
    __tablename__ = 'departments'

    # 主鍵：部門ID
    department_id = db.Column(db.Integer, primary_key=True)

    # 部門名稱：不能為空
    department_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        """
        對象的字符串表示

        Returns:
            str: 部門對象的描述
        """
        return f'<Department {self.department_name}>'

class Teacher(db.Model):
    """
    教師模型
    存儲教師的基本信息和職業數據
    """
    __tablename__ = 'teachers'

    # 主鍵：教師編號
    teacher_id = db.Column(db.String(20), primary_key=True)

    # 教師姓名：不能為空
    name = db.Column(db.String(100), nullable=False)

    # 性別：男或女，不能為空
    gender = db.Column(db.Enum('男', '女'), nullable=False)

    # 出生日期
    birth_date = db.Column(db.Date)

    # 身份證號碼
    id_number = db.Column(db.String(18))

    # 住址
    address = db.Column(db.String(200))

    # 聯繫電話
    phone = db.Column(db.String(20))

    # 電子郵箱
    email = db.Column(db.String(100))

    # 所屬部門ID：外鍵關聯到departments表
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))

    # 職位
    position = db.Column(db.String(100))

    # 入職日期
    hire_date = db.Column(db.Date)

    # 薪資
    salary = db.Column(db.Numeric(10, 2))

    # 備註
    notes = db.Column(db.Text)

    # 記錄創建時間
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    # 記錄更新時間
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯關係：教師所屬部門
    # backref='teachers' 在Department模型中創建反向關係
    department = db.relationship('Department', backref='teachers')

    def __repr__(self):
        """
        對象的字符串表示

        Returns:
            str: 教師對象的描述
        """
        return f'<Teacher {self.name}>'