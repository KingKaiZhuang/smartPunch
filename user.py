"""
使用者認證模組 - 支援密碼加密和權限管理
"""
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from db import get_connection

bcrypt = Bcrypt()


class User(UserMixin):
    """使用者類別"""
    
    def __init__(self, user_id, username, password_hash, role='user'):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin' 或 'user'
    
    def is_admin(self):
        """檢查是否為管理員"""
        return self.role == 'admin'
    
    @staticmethod
    def get(user_id):
        """根據 ID 獲取使用者"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return User(row['id'], row['username'], row['password_hash'], row.get('role', 'user'))
        return None
    
    @staticmethod
    def get_by_username(username):
        """根據使用者名稱獲取使用者"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return User(row['id'], row['username'], row['password_hash'], row.get('role', 'user'))
        return None
    
    def check_password(self, password):
        """驗證密碼"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create_user(username, password, role='user'):
        """建立新使用者（密碼會自動加密）"""
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, password_hash, role)
            )
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return User(user_id, username, password_hash, role)
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise e
    
    @staticmethod
    def update_password(username, new_password):
        """更新使用者密碼"""
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = %s",
                (password_hash, username)
            )
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            return affected_rows > 0
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            print(f"更新密碼錯誤: {e}")
            return False
    
    @staticmethod
    def update_role(username, new_role):
        """更新使用者權限"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET role = %s WHERE username = %s",
                (new_role, username)
            )
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            return affected_rows > 0
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            print(f"更新權限錯誤: {e}")
            return False
    
    @staticmethod
    def get_all_users():
        """獲取所有使用者列表"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY id")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    
    @staticmethod
    def delete_user(username):
        """刪除使用者"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            return affected_rows > 0
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            print(f"刪除使用者錯誤: {e}")
            return False