from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from . import bp
from .forms import UserForm, ChangePasswordForm, AdminChangePasswordForm
from .decorators import admin_required, can_edit_user
from app.models import User
from datetime import datetime

@bp.route('/')
@login_required
@admin_required
def list_users():
    """使用者列表路由 - 僅管理員可訪問"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 搜尋功能
    search = request.args.get('search', '')
    if search:
        users = User.query.filter(
            User.username.contains(search)
        ).paginate(page=page, per_page=per_page, error_out=False)
    else:
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('user_management/list.html',
                         title='使用者管理',
                         users=users,
                         search=search)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """新增使用者路由 - 僅管理員可訪問"""
    form = UserForm()
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                role=form.role.data,
                related_id=form.related_id.data if form.related_id.data else None,
                is_active=form.is_active.data,
                created_at=datetime.now()
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            flash(f'使用者 {user.username} 新增成功', 'success')
            return redirect(url_for('user_management.list_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'新增失敗: {str(e)}', 'danger')
    
    return render_template('user_management/edit.html',
                         title='新增使用者',
                         form=form)

@bp.route('/<int:user_id>')
@login_required
def view_user(user_id):
    """檢視使用者詳情路由"""
    user = User.query.get_or_404(user_id)
    
    # 檢查權限：管理員可以查看所有使用者，其他使用者只能查看自己
    if current_user.role != 'admin' and current_user.user_id != user_id:
        flash('您沒有權限查看此使用者資訊', 'danger')
        abort(403)
    
    return render_template('user_management/view.html',
                         title=f'使用者詳情 - {user.username}',
                         user=user)

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """編輯使用者路由"""
    user = User.query.get_or_404(user_id)
    
    # 檢查權限
    if not can_edit_user(user_id):
        flash('您沒有權限編輯此使用者', 'danger')
        abort(403)
    
    form = UserForm(user=user, obj=user)
    
    # 非管理員不能修改角色和啟用狀態
    if current_user.role != 'admin':
        form.role.render_kw = {'disabled': True}
        form.is_active.render_kw = {'disabled': True}
        form.related_id.render_kw = {'disabled': True}
    
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            
            # 只有管理員可以修改這些欄位
            if current_user.role == 'admin':
                user.role = form.role.data
                user.related_id = form.related_id.data if form.related_id.data else None
                user.is_active = form.is_active.data
            
            # 如果提供了新密碼，則更新密碼
            if form.password.data:
                user.set_password(form.password.data)
            
            user.updated_at = datetime.now()
            db.session.commit()
            flash('使用者資訊更新成功', 'success')
            
            if current_user.role == 'admin':
                return redirect(url_for('user_management.list_users'))
            else:
                return redirect(url_for('user_management.view_user', user_id=user_id))
                
        except Exception as e:
            db.session.rollback()
            flash(f'更新失敗: {str(e)}', 'danger')
    
    return render_template('user_management/edit.html',
                         title=f'編輯使用者 - {user.username}',
                         form=form,
                         user=user)

@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """刪除使用者路由 - 僅管理員可訪問"""
    user = User.query.get_or_404(user_id)
    
    # 防止刪除自己
    if user.user_id == current_user.user_id:
        flash('不能刪除自己的帳號', 'danger')
        return redirect(url_for('user_management.list_users'))
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'使用者 {username} 已成功刪除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗: {str(e)}', 'danger')
    
    return redirect(url_for('user_management.list_users'))

@bp.route('/<int:user_id>/change-password', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    """變更密碼路由"""
    user = User.query.get_or_404(user_id)
    
    # 檢查權限
    if not can_edit_user(user_id):
        flash('您沒有權限修改此使用者的密碼', 'danger')
        abort(403)
    
    # 管理員可以直接重設密碼，其他使用者需要輸入當前密碼
    if current_user.role == 'admin' and current_user.user_id != user_id:
        form = AdminChangePasswordForm()
    else:
        form = ChangePasswordForm()
    
    if form.validate_on_submit():
        try:
            # 如果是普通使用者修改自己的密碼，需要驗證當前密碼
            if hasattr(form, 'current_password'):
                if not user.check_password(form.current_password.data):
                    flash('當前密碼錯誤', 'danger')
                    return render_template('user_management/change_password.html',
                                         title='變更密碼',
                                         form=form,
                                         user=user)
            
            user.set_password(form.new_password.data)
            user.updated_at = datetime.now()
            db.session.commit()
            flash('密碼變更成功', 'success')
            
            if current_user.role == 'admin' and current_user.user_id != user_id:
                return redirect(url_for('user_management.view_user', user_id=user_id))
            else:
                return redirect(url_for('user_management.view_user', user_id=user_id))
                
        except Exception as e:
            db.session.rollback()
            flash(f'密碼變更失敗: {str(e)}', 'danger')
    
    return render_template('user_management/change_password.html',
                         title='變更密碼',
                         form=form,
                         user=user)
