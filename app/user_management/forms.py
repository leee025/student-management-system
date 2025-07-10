from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Optional
from app.models import User

class UserForm(FlaskForm):
    """使用者管理表單"""
    username = StringField('使用者名稱', validators=[
        DataRequired(message='請輸入使用者名稱'),
        Length(min=3, max=50, message='使用者名稱長度必須在3-50字符之間')
    ])
    password = PasswordField('密碼', validators=[
        Optional(),
        Length(min=6, message='密碼長度至少6個字符')
    ])
    confirm_password = PasswordField('確認密碼', validators=[
        EqualTo('password', message='兩次輸入的密碼不一致')
    ])
    role = SelectField('角色', choices=[
        ('admin', '管理員'),
        ('teacher', '教師'),
        ('student', '學生'),
        ('staff', '職員')
    ], validators=[DataRequired(message='請選擇角色')])
    related_id = StringField('關聯ID', validators=[
        Optional(),
        Length(max=20, message='關聯ID長度不能超過20個字符')
    ], description='教師ID或學生ID等')
    is_active = BooleanField('啟用狀態', default=True)
    submit = SubmitField('提交')

    def __init__(self, user=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.user = user
        
        # 如果是編輯模式，密碼為可選
        if user:
            self.password.validators = [Optional(), Length(min=6, message='密碼長度至少6個字符')]
        else:
            self.password.validators = [DataRequired(message='請輸入密碼'), Length(min=6, message='密碼長度至少6個字符')]

    def validate_username(self, field):
        """驗證使用者名稱唯一性"""
        user = User.query.filter_by(username=field.data).first()
        if user and (not self.user or user.user_id != self.user.user_id):
            raise ValidationError('該使用者名稱已被使用')

class ChangePasswordForm(FlaskForm):
    """密碼變更表單"""
    current_password = PasswordField('當前密碼', validators=[
        DataRequired(message='請輸入當前密碼')
    ])
    new_password = PasswordField('新密碼', validators=[
        DataRequired(message='請輸入新密碼'),
        Length(min=6, message='密碼長度至少6個字符')
    ])
    confirm_password = PasswordField('確認新密碼', validators=[
        DataRequired(message='請確認新密碼'),
        EqualTo('new_password', message='兩次輸入的密碼不一致')
    ])
    submit = SubmitField('變更密碼')

class AdminChangePasswordForm(FlaskForm):
    """管理員重設密碼表單"""
    new_password = PasswordField('新密碼', validators=[
        DataRequired(message='請輸入新密碼'),
        Length(min=6, message='密碼長度至少6個字符')
    ])
    confirm_password = PasswordField('確認新密碼', validators=[
        DataRequired(message='請確認新密碼'),
        EqualTo('new_password', message='兩次輸入的密碼不一致')
    ])
    submit = SubmitField('重設密碼')
