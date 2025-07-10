from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def admin_required(f):
    """裝飾器：檢查當前使用者是否為管理員"""
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

def can_edit_user(user_id):
    """檢查當前使用者是否可以編輯指定使用者"""
    if not current_user.is_authenticated:
        return False
    
    # 管理員可以編輯所有使用者
    if current_user.role == 'admin':
        return True
    
    # 使用者只能編輯自己的資料
    return str(current_user.user_id) == str(user_id)
