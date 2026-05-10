import mysql.connector
import random
# ---------- 資料庫設定 ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0000",
    "database": "personnel_data"
}

# ---------- 建立連線 ----------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------- 上班打卡 ----------
def insert_check_in(name, nid, check_in):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO service_records 
        (name, id_number, service_start, service_item, service_content, service_area, import_action)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    # 預設值
    service_item = "0020"
    service_content = "0028"
    service_area = "D"
    import_action = "A"

    cursor.execute(sql, (name, nid, check_in, service_item, service_content, service_area, import_action))
    conn.commit()
    cursor.close()
    conn.close()


# ---------- 下班打卡 ----------
def update_check_out(nid, check_out, hours, minutes):
    conn = get_connection()
    cursor = conn.cursor()

    # 1) 檢查：這個 nid 在「同一個月」是否已經有寫過 served_people_count > 0
    check_sql = """
        SELECT COUNT(*)
        FROM service_records
        WHERE id_number = %s
          AND YEAR(service_start) = YEAR(%s)
          AND MONTH(service_start) = MONTH(%s)
          AND served_people_count IS NOT NULL
          AND served_people_count > 0
    """
    cursor.execute(check_sql, (nid, check_out, check_out))
    already_has_month_value = cursor.fetchone()[0] > 0

    # 2) 若本月已寫過，就寫 0；否則本月第一次寫 15~30
    served_people_count = 0 if already_has_month_value else random.randint(15, 30)

    # 3) 更新「最新一筆未下班」紀錄（你原本 ORDER BY serial_no）
    update_sql = """
        UPDATE service_records
        SET service_end = %s,
            service_hours = %s,
            service_minutes = %s,
            served_people_count = %s
        WHERE id_number = %s AND service_end IS NULL
        ORDER BY serial_no DESC
        LIMIT 1
    """
    cursor.execute(update_sql, (check_out, hours, minutes, served_people_count, nid))
    conn.commit()

    cursor.close()
    conn.close()
    return served_people_count  # 可選：回傳，讓你主程式印出來