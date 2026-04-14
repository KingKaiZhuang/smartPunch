"""
Flask 應用程式配置和初始化
"""
from flask import Flask
from flask_login import LoginManager
from user import User


def create_app():
    """建立並配置 Flask 應用程式"""
    
    app = Flask(__name__)
    app.secret_key = "super_secret_key_123"

    # 初始化 Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # 設定登入頁面的路由
    login_manager.login_message = '請先登入以繼續'

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    return app
