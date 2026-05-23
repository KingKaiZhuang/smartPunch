import sqlitecloud
from flask_bcrypt import Bcrypt
import sys
import os

# Add parent directory to path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_connection

bcrypt = Bcrypt()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("正在建立 users 資料表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user' NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    print("正在建立 service_records 資料表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_records (
            serial_no INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50),
            id_number VARCHAR(20),
            service_start DATETIME,
            service_end DATETIME,
            service_item VARCHAR(50),
            service_content VARCHAR(50),
            service_hours INT DEFAULT 0,
            service_minutes INT DEFAULT 0,
            served_people_count INT DEFAULT 0,
            transport_fee INT DEFAULT 0,
            meal_fee INT DEFAULT 0,
            service_area VARCHAR(50),
            remarks TEXT,
            import_action VARCHAR(50),
            serial_number VARCHAR(50),
            foreign_service_count INT DEFAULT 0,
            domestic_service_count INT DEFAULT 0
        );
    """)
    
    conn.commit()
    print("資料表建立完成！")
    
    # 建立預設管理員
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_exists = cursor.fetchone()
    
    if not admin_exists:
        print("正在建立預設管理員帳號 (admin / 0000)...")
        password_hash = bcrypt.generate_password_hash("0000").decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", password_hash, "admin")
        )
        conn.commit()
        print("預設管理員建立完成！")
    else:
        print("預設管理員已經存在，略過建立。")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_db()
