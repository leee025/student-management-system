"""
用戶認證表單
定義登錄和註冊相關的WTForms表單類，包含字段驗證和自定義驗證方法
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """
    用戶登錄表單
    包含用戶名、密碼和記住我選項
    """

    # 用戶名字段：必填
    username = StringField('使用者名稱', validators=[DataRequired(message='請輸入使用者名稱')])

    # 密碼字段：必填，輸入時隱藏內容
    password = PasswordField('密碼', validators=[DataRequired(message='請輸入密碼')])

    # 記住我選項：布爾字段，用於延長會話時間
    remember_me = BooleanField('記住我')

    # 提交按鈕
    submit = SubmitField('登錄')

class RegistrationForm(FlaskForm):
    """
    用戶註冊表單
    包含用戶名和密碼，並驗證用戶名唯一性
    """

    # 用戶名字段：必填
    username = StringField('使用者名稱', validators=[DataRequired(message='請輸入使用者名稱')])

    # 密碼字段：必填，輸入時隱藏內容
    password = PasswordField('密碼', validators=[DataRequired(message='請輸入密碼')])

    # 提交按鈕
    submit = SubmitField('註冊')

    def validate_username(self, field):
        """
        自定義用戶名驗證方法
        檢查用戶名是否已存在於數據庫中

        Args:
            field: 用戶名字段對象

        Raises:
            ValidationError: 當用戶名已存在時拋出驗證錯誤
        """
        # 查詢數據庫中是否已存在該用戶名
        user = User.query.filter_by(username=field.data).first()

        # 如果用戶名已存在，拋出驗證錯誤
        if user is not None:
            raise ValidationError('該使用者名稱已被使用')