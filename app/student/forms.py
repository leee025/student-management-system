"""
學生管理表單
定義學生相關的WTForms表單類，包含字段驗證和選項設置
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError, Regexp
from app.models import Student, Class
from flask_login import current_user

class StudentForm(FlaskForm):
    """
    學生信息表單
    用於學生新增和編輯操作的表單驗證
    """

    # 學號字段：必填，長度5-20字符，只允許字母數字
    student_id = StringField('學號', validators=[
        DataRequired(message='請輸入學號'),
        Length(min=5, max=20, message='學號長度必須在5-20字符之間'),
        Regexp(r'^[A-Za-z0-9]+$', message='學號只能包含字母和數字')
    ], render_kw={"placeholder": "例如：S2024001"})

    # 姓名字段：必填，長度2-50字符
    name = StringField('姓名', validators=[
        DataRequired(message='請輸入姓名'),
        Length(min=2, max=50, message='姓名長度必須在2-50字符之間')
    ], render_kw={"placeholder": "請輸入學生姓名"})

    # 班級選擇字段：必填，選項從數據庫動態載入
    class_id = SelectField('班級', coerce=int, validators=[
        DataRequired(message='請選擇班級')
    ], render_kw={"class": "form-select"})

    def validate_class_id(self, field):
        """驗證班級選擇"""
        if field.data == 0:
            raise ValidationError('請選擇有效的班級')

    # 性別選擇字段：必填，固定選項（男/女）
    gender = SelectField('性別', choices=[
        ('', '-- 請選擇性別 --'),
        ('男', '男'),
        ('女', '女')
    ], validators=[DataRequired(message='請選擇性別')],
    render_kw={"class": "form-select"})

    # 出生日期字段：可選，日期格式YYYY-MM-DD
    birth_date = DateField('出生日期', format='%Y-%m-%d', validators=[
        Optional()
    ], render_kw={"placeholder": "YYYY-MM-DD"})

    # 身份證號字段：可選，長度驗證
    id_number = StringField('身份證號', validators=[
        Optional(),
        Length(min=10, max=18, message='身份證號長度必須在10-18字符之間')
    ], render_kw={"placeholder": "請輸入身份證號"})

    # 地址字段：可選，最大長度200字符
    address = TextAreaField('地址', validators=[
        Optional(),
        Length(max=200, message='地址長度不能超過200字符')
    ], render_kw={
        "placeholder": "請輸入詳細地址",
        "rows": 3
    })

    # 電話字段：可選，格式驗證
    phone = StringField('電話', validators=[
        Optional(),
        Length(max=20, message='電話號碼長度不能超過20字符'),
        Regexp(r'^[\d\-\+\(\)\s]+$', message='請輸入有效的電話號碼')
    ], render_kw={"placeholder": "例如：0912-345-678"})

    # 郵箱字段：可選，包含郵箱格式驗證
    email = StringField('郵箱', validators=[
        Optional(),
        Email(message='請輸入有效的郵箱地址'),
        Length(max=100, message='郵箱長度不能超過100字符')
    ], render_kw={"placeholder": "例如：student@example.com"})

    # 入學日期字段：可選，日期格式YYYY-MM-DD
    enrollment_date = DateField('入學日期', format='%Y-%m-%d', validators=[
        Optional()
    ], render_kw={"placeholder": "YYYY-MM-DD"})

    # 學籍狀態選擇字段：必填，固定選項
    status = SelectField('學籍狀態', choices=[
        ('', '-- 請選擇狀態 --'),
        ('在學', '在學'),
        ('休學', '休學'),
        ('退學', '退學'),
        ('畢業', '畢業')
    ], validators=[DataRequired(message='請選擇學籍狀態')],
    render_kw={"class": "form-select"})

    # 備註字段：可選
    notes = TextAreaField('備註', validators=[
        Optional(),
        Length(max=500, message='備註長度不能超過500字符')
    ], render_kw={
        "placeholder": "請輸入備註信息（可選）",
        "rows": 3
    })

    # 提交按鈕
    submit = SubmitField('提交')

    def __init__(self, student=None, *args, **kwargs):
        """
        表單初始化方法
        動態載入班級選項列表

        Args:
            student: 學生對象（編輯模式時使用）
            *args: 位置參數
            **kwargs: 關鍵字參數
        """
        super(StudentForm, self).__init__(*args, **kwargs)
        self.student = student

        # 根據用戶角色載入班級選項
        if current_user.role == 'admin':
            # 管理員可以看到所有班級
            self.class_id.choices = [(0, '-- 請選擇班級 --')] + [
                (c.class_id, f"{c.class_name} ({c.department.department_name if c.department else ''})")
                for c in Class.query.order_by(Class.class_name).all()
            ]
        elif current_user.role == 'teacher':
            # 教師只能看到自己負責的班級
            self.class_id.choices = [(0, '-- 請選擇班級 --')] + [
                (c.class_id, f"{c.class_name} ({c.department.department_name if c.department else ''})")
                for c in Class.query.filter_by(teacher_id=current_user.related_id).order_by(Class.class_name).all()
            ]
        else:
            # 其他角色沒有班級選項
            self.class_id.choices = [(0, '-- 無可選班級 --')]

    def validate_student_id(self, field):
        """
        驗證學號唯一性

        Args:
            field: 學號字段對象

        Raises:
            ValidationError: 當學號已存在時拋出驗證錯誤
        """
        student = Student.query.filter_by(student_id=field.data).first()
        if student and (not self.student or student.student_id != self.student.student_id):
            raise ValidationError('該學號已被使用')

    def validate_email(self, field):
        """
        驗證郵箱唯一性（如果提供）

        Args:
            field: 郵箱字段對象

        Raises:
            ValidationError: 當郵箱已被使用時拋出驗證錯誤
        """
        if field.data:
            student = Student.query.filter_by(email=field.data).first()
            if student and (not self.student or student.student_id != self.student.student_id):
                raise ValidationError('該郵箱已被使用')

class StudentSearchForm(FlaskForm):
    """
    學生搜索表單
    用於學生列表頁面的搜索功能
    """

    # 搜索關鍵字字段
    search = StringField('搜索學生', validators=[
        Optional(),
        Length(max=100, message='搜索關鍵字長度不能超過100字符')
    ], render_kw={
        "placeholder": "請輸入學號、姓名或關鍵字",
        "class": "form-control"
    })

    # 班級篩選字段
    class_filter = SelectField('篩選班級', coerce=int, validators=[
        Optional()
    ], render_kw={"class": "form-select"})

    # 性別篩選字段
    gender_filter = SelectField('篩選性別', validators=[
        Optional()
    ], choices=[
        ('', '-- 所有性別 --'),
        ('男', '男'),
        ('女', '女')
    ], render_kw={"class": "form-select"})

    # 學籍狀態篩選字段
    status_filter = SelectField('篩選狀態', validators=[
        Optional()
    ], choices=[
        ('', '-- 所有狀態 --'),
        ('在學', '在學'),
        ('休學', '休學'),
        ('退學', '退學'),
        ('畢業', '畢業')
    ], render_kw={"class": "form-select"})

    # 搜索按鈕
    submit = SubmitField('搜索')

    def __init__(self, *args, **kwargs):
        """
        表單初始化方法
        動態載入班級篩選選項
        """
        super(StudentSearchForm, self).__init__(*args, **kwargs)

        # 根據用戶角色載入班級篩選選項
        if current_user.role == 'admin':
            # 管理員可以看到所有班級
            self.class_filter.choices = [(0, '-- 所有班級 --')] + [
                (c.class_id, c.class_name)
                for c in Class.query.order_by(Class.class_name).all()
            ]
        elif current_user.role == 'teacher':
            # 教師只能看到自己負責的班級
            self.class_filter.choices = [(0, '-- 所有班級 --')] + [
                (c.class_id, c.class_name)
                for c in Class.query.filter_by(teacher_id=current_user.related_id).order_by(Class.class_name).all()
            ]
        else:
            # 其他角色沒有班級篩選選項
            self.class_filter.choices = [(0, '-- 無可選班級 --')]

