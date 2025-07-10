"""
班級管理表單
定義班級相關的WTForms表單類，包含字段驗證和選項設置
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from app.models import Class, Department, Teacher

class ClassForm(FlaskForm):
    """
    班級信息表單
    用於班級新增和編輯操作的表單驗證
    """

    # 班級名稱字段：必填，長度2-100字符
    class_name = StringField('班級名稱', validators=[
        DataRequired(message='請輸入班級名稱'),
        Length(min=2, max=100, message='班級名稱長度必須在2-100字符之間')
    ], render_kw={"placeholder": "例如：資訊工程系一年甲班"})

    # 年級字段：必填，1-6年級
    grade = IntegerField('年級', validators=[
        DataRequired(message='請輸入年級'),
        NumberRange(min=1, max=6, message='年級必須在1-6之間')
    ], render_kw={"placeholder": "請輸入年級 (1-6)"})

    # 所屬系所選擇字段：必填，選項從數據庫動態載入
    department_id = SelectField('所屬系所', coerce=int, validators=[
        DataRequired(message='請選擇所屬系所')
    ], render_kw={"class": "form-select"})

    def validate_department_id(self, field):
        """驗證系所選擇"""
        if field.data == 0:
            raise ValidationError('請選擇有效的系所')

    # 班導師選擇字段：可選，選項從數據庫動態載入
    teacher_id = SelectField('班導師', coerce=str, validators=[
        Optional()
    ], render_kw={"class": "form-select"})

    # 班級描述字段：可選
    description = TextAreaField('班級描述', validators=[
        Optional(),
        Length(max=500, message='描述長度不能超過500字符')
    ], render_kw={
        "placeholder": "請輸入班級描述（可選）",
        "rows": 3
    })

    # 提交按鈕
    submit = SubmitField('提交')

    def __init__(self, class_obj=None, *args, **kwargs):
        """
        表單初始化方法
        動態載入系所和教師選項列表

        Args:
            class_obj: 班級對象（編輯模式時使用）
            *args: 位置參數
            **kwargs: 關鍵字參數
        """
        super(ClassForm, self).__init__(*args, **kwargs)
        self.class_obj = class_obj

        # 載入系所選項
        self.department_id.choices = [(0, '-- 請選擇系所 --')] + [
            (d.department_id, d.department_name)
            for d in Department.query.order_by(Department.department_name).all()
        ]

        # 載入教師選項
        self.teacher_id.choices = [('', '-- 請選擇班導師 --')] + [
            (t.teacher_id, f"{t.name} ({t.teacher_id})")
            for t in Teacher.query.order_by(Teacher.name).all()
        ]

    def validate_class_name(self, field):
        """
        驗證班級名稱唯一性

        Args:
            field: 班級名稱字段對象

        Raises:
            ValidationError: 當班級名稱已存在時拋出驗證錯誤
        """
        class_obj = Class.query.filter_by(class_name=field.data).first()
        if class_obj and (not self.class_obj or class_obj.class_id != self.class_obj.class_id):
            raise ValidationError('該班級名稱已被使用')

    def validate_teacher_id(self, field):
        """
        驗證教師是否已擔任其他班級的班導師

        Args:
            field: 教師ID字段對象

        Raises:
            ValidationError: 當教師已擔任其他班級班導師時拋出驗證錯誤
        """
        if field.data and field.data != '':
            # 檢查該教師是否已擔任其他班級的班導師
            existing_class = Class.query.filter_by(teacher_id=field.data).first()
            if existing_class and (not self.class_obj or existing_class.class_id != self.class_obj.class_id):
                teacher = Teacher.query.get(field.data)
                teacher_name = teacher.name if teacher else field.data
                raise ValidationError(f'教師 {teacher_name} 已擔任班級 "{existing_class.class_name}" 的班導師')

class ClassSearchForm(FlaskForm):
    """
    班級搜索表單
    用於班級列表頁面的搜索功能
    """

    # 搜索關鍵字字段
    search = StringField('搜索班級', validators=[
        Optional(),
        Length(max=100, message='搜索關鍵字長度不能超過100字符')
    ], render_kw={
        "placeholder": "請輸入班級名稱或關鍵字",
        "class": "form-control"
    })

    # 系所篩選字段
    department_filter = SelectField('篩選系所', coerce=int, validators=[
        Optional()
    ], render_kw={"class": "form-select"})

    # 年級篩選字段
    grade_filter = SelectField('篩選年級', coerce=int, validators=[
        Optional()
    ], choices=[
        (0, '-- 所有年級 --'),
        (1, '一年級'),
        (2, '二年級'),
        (3, '三年級'),
        (4, '四年級'),
        (5, '五年級'),
        (6, '六年級')
    ], render_kw={"class": "form-select"})

    # 搜索按鈕
    submit = SubmitField('搜索')

    def __init__(self, *args, **kwargs):
        """
        表單初始化方法
        動態載入系所篩選選項
        """
        super(ClassSearchForm, self).__init__(*args, **kwargs)

        # 載入系所篩選選項
        self.department_filter.choices = [(0, '-- 所有系所 --')] + [
            (d.department_id, d.department_name)
            for d in Department.query.order_by(Department.department_name).all()
        ]