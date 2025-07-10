"""
班級管理路由
處理班級相關的CRUD操作和視圖函數
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from . import bp
from .forms import ClassForm
from .decorators import admin_or_teacher_required, admin_required, can_edit_class, can_view_class
from app.models import Class, Department, Teacher, Student
from datetime import datetime, timezone

@bp.route('/')
@login_required
@admin_or_teacher_required
def list_classes():
    """
    班級列表路由 - 管理員和教師可訪問
    支持搜索和分頁功能
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 搜尋功能
    search = request.args.get('search', '')
    query = Class.query.options(
        joinedload(Class.department),
        joinedload(Class.teacher)
    )
    
    if search:
        query = query.filter(
            Class.class_name.contains(search)
        )
    
    # 根據用戶角色過濾數據
    if current_user.role == 'teacher':
        # 教師只能看到自己擔任班主任的班級
        query = query.filter(Class.teacher_id == current_user.related_id)
    
    classes = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('classes/class_list.html',
                         title='班級管理',
                         classes=classes,
                         search=search)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_class():
    """新增班級路由 - 僅管理員可訪問"""
    form = ClassForm()
    
    if form.validate_on_submit():
        try:
            class_obj = Class(
                class_name=form.class_name.data,
                grade=form.grade.data,
                department_id=form.department_id.data if form.department_id.data != 0 else None,
                teacher_id=form.teacher_id.data if form.teacher_id.data != '' else None,
                created_at=datetime.now(timezone.utc)
            )
            
            db.session.add(class_obj)
            db.session.commit()
            
            flash(f'班級 "{class_obj.class_name}" 新增成功！', 'success')
            return redirect(url_for('class_management.list_classes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'新增班級時發生錯誤：{str(e)}', 'danger')
    
    return render_template('classes/form.html',
                         title='新增班級',
                         form=form,
                         action='add')

@bp.route('/<int:class_id>')
@login_required
def view_class(class_id):
    """查看班級詳情路由"""
    if not can_view_class(class_id):
        flash('您沒有權限查看此班級', 'danger')
        abort(403)
    
    class_obj = Class.query.options(
        joinedload(Class.department),
        joinedload(Class.teacher),
        joinedload(Class.students)
    ).get_or_404(class_id)
    
    return render_template('classes/detail.html',
                         title=f'班級詳情 - {class_obj.class_name}',
                         class_obj=class_obj)

@bp.route('/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    """編輯班級路由"""
    if not can_edit_class(class_id):
        flash('您沒有權限編輯此班級', 'danger')
        abort(403)
    
    class_obj = Class.query.get_or_404(class_id)
    form = ClassForm(class_obj=class_obj, obj=class_obj)
    
    if form.validate_on_submit():
        try:
            class_obj.class_name = form.class_name.data
            class_obj.grade = form.grade.data
            class_obj.department_id = form.department_id.data if form.department_id.data != 0 else None
            class_obj.teacher_id = form.teacher_id.data if form.teacher_id.data != '' else None
            class_obj.description = form.description.data
            class_obj.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'班級 "{class_obj.class_name}" 更新成功！', 'success')
            return redirect(url_for('class_management.view_class', class_id=class_id))

        except Exception as e:
            db.session.rollback()
            flash(f'更新班級時發生錯誤：{str(e)}', 'danger')
    
    return render_template('classes/form.html',
                         title=f'編輯班級 - {class_obj.class_name}',
                         form=form,
                         class_obj=class_obj,
                         action='edit')

@bp.route('/<int:class_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_class(class_id):
    """刪除班級路由 - 僅管理員可訪問"""
    class_obj = Class.query.get_or_404(class_id)
    
    try:
        # 檢查是否有學生在此班級
        if class_obj.students:
            flash(f'無法刪除班級 "{class_obj.class_name}"，因為還有學生在此班級中', 'warning')
            return redirect(url_for('class_management.list_classes'))
        
        class_name = class_obj.class_name
        db.session.delete(class_obj)
        db.session.commit()
        
        flash(f'班級 "{class_name}" 刪除成功！', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'刪除班級時發生錯誤：{str(e)}', 'danger')
    
    return redirect(url_for('class_management.list_classes'))

@bp.route('/<int:class_id>/students')
@login_required
def class_students(class_id):
    """查看班級學生列表路由"""
    if not can_view_class(class_id):
        flash('您沒有權限查看此班級', 'danger')
        abort(403)

    class_obj = Class.query.get_or_404(class_id)
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 使用 Student 查詢而不是關聯對象來實現分頁
    students = Student.query.filter_by(class_id=class_id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('classes/students.html',
                         title=f'{class_obj.class_name} - 學生列表',
                         class_obj=class_obj,
                         students=students)

@bp.route('/search')
@login_required
@admin_or_teacher_required
def search_classes():
    """班級搜索API路由"""
    query = request.args.get('q', '')
    if not query:
        return {'classes': []}
    
    classes_query = Class.query.filter(
        Class.class_name.contains(query)
    )
    
    # 根據用戶角色過濾
    if current_user.role == 'teacher':
        classes_query = classes_query.filter(Class.teacher_id == current_user.related_id)
    
    classes = classes_query.limit(10).all()
    
    return {
        'classes': [
            {
                'class_id': c.class_id,
                'class_name': c.class_name,
                'grade': c.grade,
                'department_name': c.department.department_name if c.department else None
            }
            for c in classes
        ]
    }

@bp.route('/my-class')
@login_required
def my_class():
    """
    學生查看自己班級的路由
    只有學生角色可以訪問
    """
    if current_user.role != 'student':
        flash('此功能僅限學生使用', 'warning')
        return redirect(url_for('index'))

    if not current_user.related_id:
        flash('您的賬戶尚未關聯學生資料', 'warning')
        return redirect(url_for('index'))

    # 查找學生記錄
    student = Student.query.filter_by(student_id=current_user.related_id).first()
    if not student:
        flash('找不到您的學生資料', 'danger')
        return redirect(url_for('index'))

    if not student.class_id:
        flash('您尚未分配到任何班級', 'info')
        return redirect(url_for('index'))

    # 查找班級信息
    class_obj = Class.query.options(
        joinedload(Class.department),
        joinedload(Class.teacher),
        joinedload(Class.students)
    ).get(student.class_id)

    if not class_obj:
        flash('找不到您的班級資料', 'danger')
        return redirect(url_for('index'))

    return render_template('classes/my_class.html',
                         title=f'我的班級 - {class_obj.class_name}',
                         class_obj=class_obj,
                         student=student)
