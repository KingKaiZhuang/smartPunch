import sqlitecloud
import random
from env_config import get_required_env

# ---------- 建立連線 ----------
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class SqliteCloudConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn
        
    def cursor(self, dictionary=False):
        if dictionary:
            self._conn.row_factory = dict_factory
        else:
            self._conn.row_factory = None
        return self._conn.cursor()
        
    def commit(self):
        self._conn.commit()
        
    def rollback(self):
        self._conn.rollback()
        
    def close(self):
        self._conn.close()

def get_connection():
    # 連接到 personnel_data
    conn = sqlitecloud.connect(get_required_env("SQLITECLOUD_URL"))
    return SqliteCloudConnectionWrapper(conn)

# ---------- 上班打卡 ----------
def insert_check_in(name, nid, check_in):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO service_records 
        (name, id_number, service_start, service_item, service_content, service_area, import_action)
        VALUES (?, ?, ?, ?, ?, ?, ?)
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
        WHERE id_number = ?
          AND strftime('%Y', service_start) = strftime('%Y', ?)
          AND strftime('%m', service_start) = strftime('%m', ?)
          AND served_people_count IS NOT NULL
          AND served_people_count > 0
    """
    cursor.execute(check_sql, (nid, check_out, check_out))
    already_has_month_value = cursor.fetchone()[0] > 0

    # 2) 若本月已寫過，就寫 0；否則本月第一次寫 15~30
    served_people_count = 0 if already_has_month_value else random.randint(15, 30)

    # 3) 更新「最新一筆未下班」紀錄
    update_sql = """
        UPDATE service_records
        SET service_end = ?,
            service_hours = ?,
            service_minutes = ?,
            served_people_count = ?
        WHERE serial_no = (
            SELECT serial_no 
            FROM service_records 
            WHERE id_number = ? AND service_end IS NULL 
            ORDER BY serial_no DESC 
            LIMIT 1
        )
    """
    cursor.execute(update_sql, (check_out, hours, minutes, served_people_count, nid))
    conn.commit()

    cursor.close()
    conn.close()
    return served_people_count  # 可選：回傳，讓你主程式印出來