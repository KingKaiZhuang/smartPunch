from user import User
from db import get_connection

def test():
    # 測試連線
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("Users found:", len(users))
    print(users)
    
    # 測試 User 模型
    admin = User.get_by_username('admin')
    if admin:
        print("Admin user retrieved successfully.")
        print(f"ID: {admin.id}, Username: {admin.username}, Role: {admin.role}")
        # Test password
        print("Password check (0000):", admin.check_password("0000"))
    else:
        print("Failed to retrieve admin user.")

if __name__ == "__main__":
    test()
