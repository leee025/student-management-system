"""
教師管理權限控制裝飾器
提供教師管理相關的權限檢查功能
"""

from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def admin_required(f):
    """
    裝飾器：檢查當前使用者是否為管理員
    教師管理功能只有管理員可以執行
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

def admin_or_self_required(f):
    """
    裝飾器：檢查當前使用者是否為管理員或教師本人
    教師可以查看和編輯自己的資料
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('請先登錄', 'warning')
            return redirect(url_for('auth.login'))
        
        # 管理員可以訪問所有教師資料
        if current_user.role == 'admin':
            return f(*args, **kwargs)
        
        # 教師只能訪問自己的資料
        if current_user.role == 'teacher':
            teacher_id = kwargs.get('teacher_id')
            if teacher_id and str(current_user.related_id) == str(teacher_id):
                return f(*args, **kwargs)
        
        flash('您沒有權限訪問此頁面', 'danger')
        abort(403)
    
    return decorated_function

def can_edit_teacher(teacher_id):
    """
    檢查當前使用者是否可以編輯指定教師
    
    Args:
        teacher_id: 教師ID
        
    Returns:
        bool: 是否有編輯權限
    """
    if not current_user.is_authenticated:
        return False
    
    # 管理員可以編輯所有教師
    if current_user.role == 'admin':
        return True
    
    # 教師只能編輯自己的資料
    if current_user.role == 'teacher':
        return str(current_user.related_id) == str(teacher_id)
    
    return False

def can_view_teacher(teacher_id):
    """
    檢查當前使用者是否可以查看指定教師
    
    Args:
        teacher_id: 教師ID
        
    Returns:
        bool: 是否有查看權限
    """
    if not current_user.is_authenticated:
        return False
    
    # 管理員可以查看所有教師
    if current_user.role == 'admin':
        return True
    
    # 教師只能查看自己的資料
    if current_user.role == 'teacher':
        return str(current_user.related_id) == str(teacher_id)
    
    return False

def can_view_teacher_list():
    """
    檢查當前使用者是否可以查看教師列表
    
    Returns:
        bool: 是否有查看權限
    """
    if not current_user.is_authenticated:
        return False
    
    # 只有管理員可以查看教師列表
    return current_user.role == 'admin'

def filter_teachers_by_permission(query):
    """
    根據用戶權限過濾教師查詢
    
    Args:
        query: SQLAlchemy查詢對象
        
    Returns:
        query: 過濾後的查詢對象
    """
    if not current_user.is_authenticated:
        return query.filter(False)  # 返回空結果
    
    # 管理員可以查看所有教師
    if current_user.role == 'admin':
        return query
    
    # 教師只能查看自己
    if current_user.role == 'teacher':
        return query.filter_by(teacher_id=current_user.related_id)
    
    return query.filter(False)  # 其他角色返回空結果
