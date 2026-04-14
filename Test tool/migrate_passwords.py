"""
密碼加密遷移工具
用於將現有的明文密碼轉換為加密密碼
"""
from flask_bcrypt import Bcrypt
from db import get_connection

bcrypt = Bcrypt()


def create_users_table():
    """建立新的使用者資料表（如果不存在）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 檢查資料表是否存在
    cursor.execute("SHOW TABLES LIKE 'users'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        # 建立新資料表
        create_table_sql = """
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('admin', 'user') DEFAULT 'user' NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ 已建立 users 資料表")
    else:
        # 檢查是否有 password_hash 欄位
        cursor.execute("SHOW COLUMNS FROM users LIKE 'password_hash'")
        column_exists = cursor.fetchone()
        
        if not column_exists:
            # 新增 password_hash 欄位
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
            conn.commit()
            print("✅ 已在 users 資料表新增 password_hash 欄位")
        
        # 檢查是否有 role 欄位
        cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
        role_exists = cursor.fetchone()
        
        if not role_exists:
            # 新增 role 欄位
            cursor.execute("ALTER TABLE users ADD COLUMN role ENUM('admin', 'user') DEFAULT 'user' NOT NULL")
            conn.commit()
            print("✅ 已在 users 資料表新增 role 欄位")
        
        print("ℹ️  users 資料表已存在且結構正確")
    
    cursor.close()
    conn.close()


def migrate_passwords():
    """將明文密碼轉換為加密密碼"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 獲取所有有明文密碼的使用者
        cursor.execute("SELECT id, username, password FROM users WHERE password IS NOT NULL")
        users = cursor.fetchall()
        
        if not users:
            print("ℹ️  沒有需要遷移的明文密碼")
            cursor.close()
            conn.close()
            return
        
        migrated_count = 0
        for user in users:
            # 加密明文密碼
            password_hash = bcrypt.generate_password_hash(user['password']).decode('utf-8')
            
            # 更新資料庫
            cursor.execute(
                "UPDATE users SET password_hash = %s, password = NULL WHERE id = %s",
                (password_hash, user['id'])
            )
            migrated_count += 1
            print(f"✅ 已遷移使用者: {user['username']}")
        
        conn.commit()
        print(f"\n🎉 成功遷移 {migrated_count} 個使用者的密碼")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 遷移失敗: {e}")
    finally:
        cursor.close()
        conn.close()


def create_admin_user():
    """建立預設管理員帳號"""
    from user import User
    
    try:
        # 檢查是否已存在 admin 使用者
        existing_user = User.get_by_username('admin')
        
        if existing_user:
            print("ℹ️  admin 使用者已存在")
            update = input("是否要重設 admin 密碼？(y/n): ").strip().lower()
            if update == 'y':
                User.update_password('admin', '0000')
                print("✅ admin 密碼已重設為 0000")
        else:
            # 建立新的 admin 使用者
            User.create_user('admin', '0000')
            print("✅ 已建立 admin 使用者（密碼: 0000）")
            
    except Exception as e:
        print(f"❌ 建立管理員失敗: {e}")


def main():
    """主程式"""
    print("=" * 50)
    print("🔐 密碼加密遷移工具")
    print("=" * 50)
    print()
    
    # 1. 建立或更新資料表結構
    print("步驟 1: 檢查資料表結構...")
    create_users_table()
    print()
    
    # 2. 遷移現有密碼
    print("步驟 2: 遷移現有密碼...")
    migrate_passwords()
    print()
    
    # 3. 建立或更新管理員帳號
    print("步驟 3: 設定管理員帳號...")
    create_admin_user()
    print()
    
    print("=" * 50)
    print("✨ 遷移完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()