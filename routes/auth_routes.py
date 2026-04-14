"""
登入/登出/註冊相關路由 - 使用加密密碼
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from user import User


def register_auth_routes(app):
    """註冊認證相關的路由"""
    
    # ----------- 登入頁面 -----------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.get_by_username(username)
            
            # 使用 check_password 方法驗證密碼
            if user and user.check_password(password):
                login_user(user)
                flash('登入成功！', 'success')
                return redirect(url_for('admin_panel'))
            else:
                flash('帳號或密碼錯誤！', 'error')
        
        return render_template('login.html')

    # ----------- 註冊頁面 -----------
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            # 獲取表單資料
            new_username = request.form.get('username')
            new_password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            role = request.form.get('role')  # 'admin' 或 'user'
            admin_username = request.form.get('admin_username')
            admin_password = request.form.get('admin_password')
            
            # 驗證欄位完整性
            if not all([new_username, new_password, confirm_password, role, admin_username, admin_password]):
                flash('請填寫所有欄位！', 'error')
                return render_template('register.html')
            
            # 驗證密碼一致性
            if new_password != confirm_password:
                flash('兩次輸入的密碼不一致！', 'error')
                return render_template('register.html')
            
            # 驗證密碼長度
            if len(new_password) < 4:
                flash('密碼至少需要 4 個字元！', 'error')
                return render_template('register.html')
            
            # 驗證管理員身份
            admin_user = User.get_by_username(admin_username)
            if not admin_user or not admin_user.check_password(admin_password):
                flash('管理員帳號或密碼錯誤！無法註冊', 'error')
                return render_template('register.html')
            
            if not admin_user.is_admin():
                flash('只有管理員才能授權註冊新使用者！', 'error')
                return render_template('register.html')
            
            # 檢查使用者名稱是否已存在
            existing_user = User.get_by_username(new_username)
            if existing_user:
                flash('此使用者名稱已被使用！', 'error')
                return render_template('register.html')
            
            # 建立新使用者
            try:
                User.create_user(new_username, new_password, role)
                flash(f'✅ 成功註冊新使用者：{new_username} ({role})！', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'註冊失敗：{str(e)}', 'error')
                return render_template('register.html')
        
        return render_template('register.html')

    # ----------- 登出 -----------
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('已登出！', 'success')
        return redirect(url_for('login'))