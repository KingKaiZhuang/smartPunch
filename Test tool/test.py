from datetime import datetime, timedelta, time
import mysql.connector

# ---------- 資料庫設定 ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0000",
    "database": "personnel_data"
}

# ---------- 固定資料 ----------
# 名字與身分證一一對應
EMPLOYEES = {
    "王小明": "A123456789",
    "林佳蓉": "B987654321",
    "張志豪": "C112233445",
    "李怡君": "D556677889",
    "陳威廷": "E998877665"
}

# ---------- 寫入資料 ----------
def insert_custom_range_data(start_date, end_date):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for name, nid in EMPLOYEES.items():
        print(f"👤 建立 {name}（{nid}）的打卡紀錄...")

        current_date = start_date
        while current_date <= end_date:
            # 上下班時間
            service_start = datetime.combine(current_date, time(8, 0))
            service_end = datetime.combine(current_date, time(17, 0))
            service_hours = 9
            service_minutes = 0

            sql = """
                INSERT INTO service_records
                (name, id_number, service_start, service_end, service_hours, service_minutes, service_item, service_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (name, nid, service_start, service_end, service_hours, service_minutes, "0010", "0001")
            cursor.execute(sql, values)

            current_date += timedelta(days=1)

        conn.commit()
        print(f"✅ 已完成 {name} 的 {start_date.strftime('%Y/%m/%d')} ~ {end_date.strftime('%Y/%m/%d')} 資料\n")

    cursor.close()
    conn.close()
    print("🎉 全部資料新增完成！")

# ---------- 主程式 ----------
if __name__ == "__main__":
    print("📅 請輸入要建立的日期區間")
    start_str = input("開始日期 (格式: YYYY-MM-DD)：").strip()
    end_str = input("結束日期 (格式: YYYY-MM-DD)：").strip()

    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

        if end_date < start_date:
            print("❌ 結束日期不能早於開始日期！")
        else:
            insert_custom_range_data(start_date, end_date)
    except ValueError:
        print("❌ 日期格式錯誤，請使用 YYYY-MM-DD 格式！")
