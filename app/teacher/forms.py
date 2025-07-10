"""
教師管理表單
定義教師相關的WTForms表單類，包含字段驗證和選項設置
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError, Regexp, NumberRange
from app.models import Teacher, Department

class TeacherForm(FlaskForm):
    """
    教師信息表單
    用於教師新增和編輯操作的表單驗證
    """

    # 教師編號字段：必填，長度3-20字符，只允許字母數字
    teacher_id = StringField('教師編號', validators=[
        DataRequired(message='請輸入教師編號'),
        Length(min=3, max=20, message='教師編號長度必須在3-20字符之間'),
        Regexp(r'^[A-Za-z0-9]+$', message='教師編號只能包含字母和數字')
    ], render_kw={"placeholder": "例如：t001 或 T2024001"})

    # 姓名字段：必填，長度2-50字符
    name = StringField('姓名', validators=[
        DataRequired(message='請輸入姓名'),
        Length(min=2, max=50, message='姓名長度必須在2-50字符之間')
    ], render_kw={"placeholder": "請輸入教師姓名"})

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
    ], render_kw={"placeholder": "例如：teacher@example.com"})

    # 所屬系所選擇字段：必填，選項從數據庫動態載入
    department_id = SelectField('所屬系所', coerce=int, validators=[
        DataRequired(message='請選擇所屬系所')
    ], render_kw={"class": "form-select"})

    def validate_department_id(self, field):
        """驗證系所選擇"""
        if field.data == 0:
            raise ValidationError('請選擇有效的系所')

    # 職位字段：可選，最大長度50字符
    position = StringField('職位', validators=[
        Optional(),
        Length(max=50, message='職位長度不能超過50字符')
    ], render_kw={"placeholder": "例如：教授、副教授、講師"})

    # 入職日期字段：必填，日期格式YYYY-MM-DD
    hire_date = DateField('入職日期', format='%Y-%m-%d', validators=[
        DataRequired(message='請選擇入職日期')
    ], render_kw={"placeholder": "YYYY-MM-DD"})

    # 薪資字段：可選，數值範圍驗證
    salary = DecimalField('薪資', validators=[
        Optional(),
        NumberRange(min=0, message='薪資不能為負數')
    ], render_kw={"placeholder": "請輸入薪資金額", "step": "0.01"})

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

    def __init__(self, teacher=None, *args, **kwargs):
        """
        表單初始化方法
        動態載入系所選項列表

        Args:
            teacher: 教師對象（編輯模式時使用）
            *args: 位置參數
            **kwargs: 關鍵字參數
        """
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.teacher = teacher

        # 載入系所選項
        self.department_id.choices = [(0, '-- 請選擇系所 --')] + [
            (d.department_id, d.department_name)
            for d in Department.query.order_by(Department.department_name).all()
        ]

    def validate_teacher_id(self, field):
        """
        驗證教師編號唯一性

        Args:
            field: 教師編號字段對象

        Raises:
            ValidationError: 當教師編號已存在時拋出驗證錯誤
        """
        teacher = Teacher.query.filter_by(teacher_id=field.data).first()
        if teacher and (not self.teacher or teacher.teacher_id != self.teacher.teacher_id):
            raise ValidationError('該教師編號已被使用')

    def validate_email(self, field):
        """
        驗證郵箱唯一性（如果提供）

        Args:
            field: 郵箱字段對象

        Raises:
            ValidationError: 當郵箱已被使用時拋出驗證錯誤
        """
        if field.data:
            teacher = Teacher.query.filter_by(email=field.data).first()
            if teacher and (not self.teacher or teacher.teacher_id != self.teacher.teacher_id):
                raise ValidationError('該郵箱已被使用')

class TeacherSearchForm(FlaskForm):
    """
    教師搜索表單
    用於教師列表頁面的搜索功能
    """

    # 搜索關鍵字字段
    search = StringField('搜索教師', validators=[
        Optional(),
        Length(max=100, message='搜索關鍵字長度不能超過100字符')
    ], render_kw={
        "placeholder": "請輸入教師編號、姓名或關鍵字",
        "class": "form-control"
    })

    # 系所篩選字段
    department_filter = SelectField('篩選系所', coerce=int, validators=[
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

    # 職位篩選字段
    position_filter = StringField('篩選職位', validators=[
        Optional(),
        Length(max=50, message='職位長度不能超過50字符')
    ], render_kw={
        "placeholder": "請輸入職位關鍵字",
        "class": "form-control"
    })

    # 搜索按鈕
    submit = SubmitField('搜索')

    def __init__(self, *args, **kwargs):
        """
        表單初始化方法
        動態載入系所篩選選項
        """
        super(TeacherSearchForm, self).__init__(*args, **kwargs)

        # 載入系所篩選選項
        self.department_filter.choices = [(0, '-- 所有系所 --')] + [
            (d.department_id, d.department_name)
            for d in Department.query.order_by(Department.department_name).all()
        ]
