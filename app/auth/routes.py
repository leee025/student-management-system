"""
用戶認證路由
處理用戶登錄、註冊、登出等認證相關的路由和視圖函數
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用戶登錄視圖
    處理用戶登錄的GET和POST請求

    Returns:
        str: GET請求返回登錄表單頁面
             POST請求成功後重定向到指定頁面或默認頁面

    路由:
        GET /auth/login - 顯示登錄表單
        POST /auth/login - 處理登錄提交
    """
    # 如果用戶已登錄，直接重定向到主頁
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # 創建登錄表單實例
    form = LoginForm()

    # 處理POST請求（表單提交）
    if form.validate_on_submit():
        # 根據用戶名查找用戶
        user = User.query.filter_by(username=form.username.data).first()

        # 驗證用戶存在且密碼正確
        if user is None or not user.check_password(form.password.data):
            flash('使用者名稱或密碼錯誤')
            return redirect(url_for('auth.login'))

        # 登錄用戶，設置記住我選項
        login_user(user, remember=form.remember_me.data)

        # 處理登錄後的重定向
        next_page = request.args.get('next')  # 獲取原本要訪問的頁面

        # 安全檢查：確保重定向URL是安全的（同域名）
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')  # 默認重定向頁面

        # 調試日誌
        print(f"登录成功，重定向到: {next_page}, 用户角色: {current_user.role}")
        return redirect(next_page)

    # GET請求或表單驗證失敗時，顯示登錄頁面
    return render_template('auth/login.html', title='登錄', form=form)

@bp.route('/logout')
def logout():
    """
    用戶登出視圖
    清除用戶會話並重定向到登錄頁面

    Returns:
        str: 重定向到登錄頁面

    路由:
        GET /auth/logout - 用戶登出
    """
    # 使用Flask-Login的logout_user函數清除用戶會話
    logout_user()

    # 重定向到登錄頁面
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用戶註冊視圖
    處理新用戶註冊的GET和POST請求

    Returns:
        str: GET請求返回註冊表單頁面
             POST請求成功後重定向到登錄頁面

    路由:
        GET /auth/register - 顯示註冊表單
        POST /auth/register - 處理註冊提交
    """
    # 如果用戶已登錄，直接重定向到主頁
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # 創建註冊表單實例
    form = RegistrationForm()

    # 處理POST請求（表單提交）
    if form.validate_on_submit():
        # 創建新用戶對象
        user = User(username=form.username.data)

        # 設置密碼（會自動進行哈希加密）
        user.set_password(form.password.data)

        # 添加到數據庫會話並提交
        db.session.add(user)
        db.session.commit()

        # 顯示成功消息
        flash('註冊成功！請登錄')

        # 重定向到登錄頁面
        return redirect(url_for('auth.login'))

    # GET請求或表單驗證失敗時，顯示註冊頁面
    return render_template('auth/register.html', title='註冊', form=form)