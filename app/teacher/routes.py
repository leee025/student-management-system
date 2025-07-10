"""
教師管理路由
處理教師相關的CRUD操作和視圖函數
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.teacher import bp
from app.teacher.forms import TeacherForm, TeacherSearchForm
from app.teacher.decorators import (admin_required, admin_or_self_required,
                        can_edit_teacher, can_view_teacher,
                        can_view_teacher_list, filter_teachers_by_permission)
from app.models import Teacher, Department
from datetime import datetime

@bp.route('/')
@login_required
def list_teachers():
    """
    教師列表路由 - 根據用戶角色顯示相應的教師
    支持搜索和分頁功能
    """
    if not can_view_teacher_list():
        flash('您沒有權限查看教師列表', 'danger')
        abort(403)

    page = request.args.get('page', 1, type=int)
    per_page = 10

    # 搜尋功能
    search = request.args.get('search', '')
    department_filter = request.args.get('department_filter', '', type=int)

    # 基礎查詢，包含關聯載入
    query = Teacher.query.options(joinedload(Teacher.department))

    # 根據用戶權限過濾數據
    query = filter_teachers_by_permission(query)

    # 應用搜索條件
    if search:
        query = query.filter(
            Teacher.name.contains(search) |
            Teacher.teacher_id.contains(search) |
            Teacher.email.contains(search) |
            Teacher.phone.contains(search) |
            Teacher.position.contains(search)
        )

    # 應用系所篩選
    if department_filter and department_filter != 0:
        query = query.filter(Teacher.department_id == department_filter)

    teachers = query.paginate(page=page, per_page=per_page, error_out=False)

    # 獲取系所選項用於篩選
    departments = Department.query.all()

    return render_template('teacher/teacher_list.html',
                         title='教師管理',
                         teachers=teachers,
                         search=search,
                         department_filter=department_filter,
                         departments=departments)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_teacher():
    """新增教師路由 - 僅管理員可訪問"""
    form = TeacherForm()

    if form.validate_on_submit():
        try:
            teacher = Teacher(
                teacher_id=form.teacher_id.data,
                name=form.name.data,
                gender=form.gender.data,
                birth_date=form.birth_date.data,
                id_number=form.id_number.data,
                address=form.address.data,
                phone=form.phone.data,
                email=form.email.data,
                department_id=form.department_id.data if form.department_id.data != 0 else None,
                position=form.position.data,
                hire_date=form.hire_date.data,
                salary=form.salary.data,
                notes=form.notes.data,
                created_at=datetime.utcnow()
            )

            db.session.add(teacher)
            db.session.commit()

            flash(f'教師 "{teacher.name}" 新增成功！', 'success')
            return redirect(url_for('teacher_management.list_teachers'))

        except Exception as e:
            db.session.rollback()
            flash(f'新增教師時發生錯誤：{str(e)}', 'danger')

    return render_template('teacher/form.html',
                         title='新增教師',
                         form=form,
                         action='add')

@bp.route('/<teacher_id>')
@login_required
@admin_or_self_required
def view_teacher(teacher_id):
    """查看教師詳情路由"""
    teacher = Teacher.query.options(
        joinedload(Teacher.department)
    ).get_or_404(teacher_id)

    return render_template('teacher/detail.html',
                         title=f'教師詳情 - {teacher.name}',
                         teacher=teacher)

@bp.route('/<teacher_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_or_self_required
def edit_teacher(teacher_id):
    """編輯教師路由"""
    teacher = Teacher.query.get_or_404(teacher_id)
    form = TeacherForm(teacher=teacher, obj=teacher)

    if form.validate_on_submit():
        try:
            teacher.teacher_id = form.teacher_id.data
            teacher.name = form.name.data
            teacher.gender = form.gender.data
            teacher.birth_date = form.birth_date.data
            teacher.id_number = form.id_number.data
            teacher.address = form.address.data
            teacher.phone = form.phone.data
            teacher.email = form.email.data
            teacher.department_id = form.department_id.data if form.department_id.data != 0 else None
            teacher.position = form.position.data
            teacher.hire_date = form.hire_date.data
            teacher.salary = form.salary.data
            teacher.notes = form.notes.data
            teacher.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'教師 "{teacher.name}" 更新成功！', 'success')
            return redirect(url_for('teacher_management.view_teacher', teacher_id=teacher_id))

        except Exception as e:
            db.session.rollback()
            flash(f'更新教師時發生錯誤：{str(e)}', 'danger')

    return render_template('teacher/form.html',
                         title=f'編輯教師 - {teacher.name}',
                         form=form,
                         teacher=teacher,
                         action='edit')

@bp.route('/<teacher_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_teacher(teacher_id):
    """刪除教師路由 - 僅管理員可訪問"""
    teacher = Teacher.query.get_or_404(teacher_id)

    try:
        teacher_name = teacher.name
        db.session.delete(teacher)
        db.session.commit()

        flash(f'教師 "{teacher_name}" 刪除成功！', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'刪除教師時發生錯誤：{str(e)}', 'danger')

    return redirect(url_for('teacher_management.list_teachers'))

@bp.route('/search')
@login_required
def search_teachers():
    """教師搜索API路由"""
    if not can_view_teacher_list():
        return {'teachers': []}

    query_text = request.args.get('q', '')
    if not query_text:
        return {'teachers': []}

    # 基礎查詢
    query = Teacher.query.options(joinedload(Teacher.department))

    # 根據用戶權限過濾數據
    query = filter_teachers_by_permission(query)

    # 應用搜索條件
    query = query.filter(
        Teacher.name.contains(query_text) |
        Teacher.teacher_id.contains(query_text)
    )

    teachers = query.limit(10).all()

    return {
        'teachers': [
            {
                'teacher_id': t.teacher_id,
                'name': t.name,
                'department_name': t.department.department_name if t.department else None,
                'position': t.position
            }
            for t in teachers
        ]
    }