"""
班級管理權限控制裝飾器
提供班級管理相關的權限檢查功能
"""

from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def admin_or_teacher_required(f):
    """
    裝飾器：檢查當前使用者是否為管理員或教師
    只有管理員和教師可以管理班級
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

def can_edit_class(class_id):
    """
    檢查當前使用者是否可以編輯指定班級
    
    Args:
        class_id: 班級ID
        
    Returns:
        bool: 是否有編輯權限
    """
    if not current_user.is_authenticated:
        return False
    
    # 管理員可以編輯所有班級
    if current_user.role == 'admin':
        return True
    
    # 教師只能編輯自己擔任班主任的班級
    if current_user.role == 'teacher':
        from app.models import Class
        class_obj = Class.query.get(class_id)
        if class_obj and class_obj.teacher_id == current_user.related_id:
            return True
    
    return False

def can_view_class(class_id):
    """
    檢查當前使用者是否可以查看指定班級
    
    Args:
        class_id: 班級ID
        
    Returns:
        bool: 是否有查看權限
    """
    if not current_user.is_authenticated:
        return False
    
    # 管理員和教師可以查看所有班級
    if current_user.role in ['admin', 'teacher']:
        return True
    
    # 學生只能查看自己所在的班級
    if current_user.role == 'student':
        from app.models import Student
        student = Student.query.filter_by(student_id=current_user.related_id).first()
        if student and str(student.class_id) == str(class_id):
            return True
    
    return False
