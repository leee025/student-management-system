"""
學生管理權限控制裝飾器
提供學生管理相關的權限檢查功能
"""

from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def admin_or_teacher_required(f):
    """
    裝飾器：檢查當前使用者是否為管理員或教師
    只有管理員和教師可以管理學生
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('請先登錄', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role not in ['admin', 'teacher']:
            flash('您沒有權限訪問此頁面', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    裝飾器：檢查當前使用者是否為管理員
    某些敏感操作只有管理員可以執行
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('請先登錄', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('您沒有權限訪問此頁面', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def can_edit_student(student_id):
    """
    檢查當前使用者是否可以編輯指定學生
    
    Args:
        student_id: 學生ID
        
    Returns:
        bool: 是否有編輯權限
    """
    if not current_user.is_authenticated:
        return False
    
    # 管理員可以編輯所有學生
    if current_user.role == 'admin':
        return True
    
    # 教師可以編輯自己班級的學生
    if current_user.role == 'teacher':
        from app.models import Student, Class
        student = Student.query.get(student_id)
        if student and student.class_info:
            return student.class_info.teacher_id == current_user.related_id
    
    # 學生只能編輯自己的資料
    if current_user.role == 'student':
        return str(current_user.related_id) == str(student_id)
    
    return False

def can_view_student(student_id):
    """
    檢查當前使用者是否可以查看指定學生
    
    Args:
        student_id: 學生ID
        
    Returns:
        bool: 是否有查看權限
    """
    if not current_user.is_authenticated:
        return False
    
    # 管理員可以查看所有學生
    if current_user.role == 'admin':
        return True
    
    # 教師可以查看自己班級的學生
    if current_user.role == 'teacher':
        from app.models import Student, Class
        student = Student.query.get(student_id)
        if student and student.class_info:
            return student.class_info.teacher_id == current_user.related_id
    
    # 學生只能查看自己的資料
    if current_user.role == 'student':
        return str(current_user.related_id) == str(student_id)
    
    return False

def can_view_student_list():
    """
    檢查當前使用者是否可以查看學生列表
    
    Returns:
        bool: 是否有查看權限
    """
    if not current_user.is_authenticated:
        return False
    
    # 管理員和教師可以查看學生列表
    return current_user.role in ['admin', 'teacher']

def filter_students_by_permission(query):
    """
    根據用戶權限過濾學生查詢
    
    Args:
        query: SQLAlchemy查詢對象
        
    Returns:
        query: 過濾後的查詢對象
    """
    if not current_user.is_authenticated:
        return query.filter(False)  # 返回空結果
    
    # 管理員可以查看所有學生
    if current_user.role == 'admin':
        return query
    
    # 教師只能查看自己班級的學生
    if current_user.role == 'teacher':
        from app.models import Class
        return query.join(Class).filter(Class.teacher_id == current_user.related_id)
    
    # 學生只能查看自己
    if current_user.role == 'student':
        return query.filter_by(student_id=current_user.related_id)
    
    return query.filter(False)  # 其他角色返回空結果
