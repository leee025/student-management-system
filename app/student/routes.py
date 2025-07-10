"""
學生管理路由
處理學生相關的CRUD操作和視圖函數
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.student import bp
from app.student.forms import StudentForm
from app.student.decorators import (admin_or_teacher_required, admin_required,
                        can_edit_student, can_view_student,
                        can_view_student_list, filter_students_by_permission)
from app.models import Student, Class
from datetime import datetime

@bp.route('/')
@login_required
def list_students():
    """
    學生列表路由 - 根據用戶角色顯示相應的學生
    支持搜索和分頁功能
    """
    if not can_view_student_list():
        flash('您沒有權限查看學生列表', 'danger')
        abort(403)

    page = request.args.get('page', 1, type=int)
    per_page = 10

    # 搜尋功能
    search = request.args.get('search', '')
    class_filter = request.args.get('class_filter', '', type=int)
    status_filter = request.args.get('status_filter', '')

    # 基礎查詢，包含關聯載入
    query = Student.query.options(joinedload(Student.class_info))

    # 根據用戶權限過濾數據
    query = filter_students_by_permission(query)

    # 應用搜索條件
    if search:
        query = query.filter(
            Student.name.contains(search) |
            Student.student_id.contains(search) |
            Student.email.contains(search) |
            Student.phone.contains(search)
        )

    # 應用班級篩選
    if class_filter and class_filter != 0:
        query = query.filter(Student.class_id == class_filter)

    # 應用狀態篩選
    if status_filter:
        query = query.filter(Student.status == status_filter)

    students_pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 獲取班級選項用於篩選
    classes = []
    if current_user.role == 'admin':
        classes = Class.query.all()
    elif current_user.role == 'teacher':
        classes = Class.query.filter_by(teacher_id=current_user.related_id).all()

    return render_template('student/student_list.html',
                         title='學生管理',
                         students=students_pagination,
                         pagination=students_pagination,
                         search=search,
                         class_filter=class_filter,
                         status_filter=status_filter,
                         classes=classes)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_or_teacher_required
def add_student():
    """新增學生路由 - 管理員和教師可訪問"""
    form = StudentForm()

    if form.validate_on_submit():
        try:
            student = Student(
                student_id=form.student_id.data,
                name=form.name.data,
                class_id=form.class_id.data if form.class_id.data != 0 else None,
                gender=form.gender.data,
                birth_date=form.birth_date.data,
                address=form.address.data,
                phone=form.phone.data,
                email=form.email.data,
                enrollment_date=form.enrollment_date.data,
                status=form.status.data,
                id_number=form.id_number.data,
                created_at=datetime.utcnow()
            )

            db.session.add(student)
            db.session.commit()

            flash(f'學生 "{student.name}" 新增成功！', 'success')
            return redirect(url_for('student_management.list_students'))

        except Exception as e:
            db.session.rollback()
            flash(f'新增學生時發生錯誤：{str(e)}', 'danger')

    return render_template('student/form.html',
                         title='新增學生',
                         form=form,
                         action='add')

@bp.route('/<student_id>')
@login_required
def view_student(student_id):
    """查看學生詳情路由"""
    if not can_view_student(student_id):
        flash('您沒有權限查看此學生', 'danger')
        abort(403)

    student = Student.query.options(
        joinedload(Student.class_info)
    ).get_or_404(student_id)

    return render_template('student/detail.html',
                         title=f'學生詳情 - {student.name}',
                         student=student)

@bp.route('/<student_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """編輯學生路由"""
    if not can_edit_student(student_id):
        flash('您沒有權限編輯此學生', 'danger')
        abort(403)

    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)

    if form.validate_on_submit():
        try:
            student.student_id = form.student_id.data
            student.name = form.name.data
            student.class_id = form.class_id.data if form.class_id.data != 0 else None
            student.gender = form.gender.data
            student.birth_date = form.birth_date.data
            student.address = form.address.data
            student.phone = form.phone.data
            student.email = form.email.data
            student.enrollment_date = form.enrollment_date.data
            student.status = form.status.data
            student.id_number = form.id_number.data
            student.notes = form.notes.data
            student.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'學生 "{student.name}" 更新成功！', 'success')
            return redirect(url_for('student_management.view_student', student_id=student_id))

        except Exception as e:
            db.session.rollback()
            flash(f'更新學生時發生錯誤：{str(e)}', 'danger')

    return render_template('student/form.html',
                         title=f'編輯學生 - {student.name}',
                         form=form,
                         student=student,
                         action='edit')

@bp.route('/<student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    """刪除學生路由 - 僅管理員可訪問"""
    student = Student.query.get_or_404(student_id)

    try:
        student_name = student.name
        db.session.delete(student)
        db.session.commit()

        flash(f'學生 "{student_name}" 刪除成功！', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'刪除學生時發生錯誤：{str(e)}', 'danger')

    return redirect(url_for('student_management.list_students'))

@bp.route('/search')
@login_required
def search_students():
    """學生搜索API路由"""
    if not can_view_student_list():
        return {'students': []}

    query_text = request.args.get('q', '')
    if not query_text:
        return {'students': []}

    # 基礎查詢
    query = Student.query.options(joinedload(Student.class_info))

    # 根據用戶權限過濾數據
    query = filter_students_by_permission(query)

    # 應用搜索條件
    query = query.filter(
        Student.name.contains(query_text) |
        Student.student_id.contains(query_text)
    )

    students = query.limit(10).all()

    return {
        'students': [
            {
                'student_id': s.student_id,
                'name': s.name,
                'class_name': s.class_info.class_name if s.class_info else None,
                'status': s.status
            }
            for s in students
        ]
    }