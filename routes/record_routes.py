"""
服務記錄查詢和管理相關路由
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from db import get_connection


def register_record_routes(app):
    """註冊服務記錄相關的路由"""
    
    # ----------- 後台主頁 -----------
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    @login_required
    def admin_panel():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # --- 基本參數 ---
        all_records_page = request.args.get('all_records_page', 1, type=int)
        per_page = 30

        # --- 獲取所有記錄 ---
        cursor.execute("SELECT * FROM service_records ORDER BY serial_no DESC")
        all_records_data = cursor.fetchall()
        
        # --- 計算分頁 ---
        total_all_records = len(all_records_data)
        total_all_pages = max(1, (total_all_records + per_page - 1) // per_page)
        all_records_page = max(1, min(all_records_page, total_all_pages))
        
        # --- 對記錄進行分頁 ---
        start_idx_all = (all_records_page - 1) * per_page
        end_idx_all = start_idx_all + per_page
        records = all_records_data[start_idx_all:end_idx_all]
        
        cursor.close()
        conn.close()

        return render_template(
            'index.html',
            records=records,
            user=current_user.username,
            all_records_page=all_records_page,
            total_all_pages=total_all_pages,
            total_all_records=total_all_records
        )

    # ----------- 搜尋頁面 -----------
    @app.route('/search', methods=['GET', 'POST'])
    @login_required
    def search_page():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # --- 基本參數 ---
        nid = request.args.get('nid', '').strip()
        name = request.args.get('name', '').strip()
        date_start = request.args.get('date_start')
        date_end = request.args.get('date_end')
        page = request.args.get('page', 1, type=int)
        per_page = 30

        print(f"搜尋參數：nid={nid}, name={name}, date_start={date_start}, date_end={date_end}")

        # --- 驗證日期格式 ---
        for var_name, var_value in [('開始日期', date_start), ('結束日期', date_end)]:
            if var_value:
                try:
                    datetime.strptime(var_value, '%Y-%m-%d')
                except ValueError:
                    flash(f'{var_name}格式不正確', 'error')
                    if var_name == '開始日期': date_start = None
                    else: date_end = None

        # --- 組合查詢 ---
        query = """
            SELECT serial_no, name, id_number, service_start, service_end,
                   service_item, service_content, service_hours, service_minutes,
                   served_people_count, transport_fee, meal_fee, service_area,
                   remarks, import_action, serial_number, foreign_service_count, domestic_service_count
            FROM service_records
            WHERE 1=1
        """
        params = []

        if nid:
            query += " AND LOWER(id_number) = LOWER(?)"
            params.append(nid)
            
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")

        if date_start and date_end:
            query += " AND DATE(service_start) BETWEEN ? AND ?"
            params.extend([date_start, date_end])
        elif date_start:
            query += " AND DATE(service_start) >= ?"
            params.append(date_start)
        elif date_end:
            query += " AND DATE(service_start) <= ?"
            params.append(date_end)

        query += " ORDER BY service_start DESC"

        # --- 執行查詢 ---
        cursor.execute(query, tuple(params))
        all_records = cursor.fetchall()

        # --- 分頁 ---
        total_records = len(all_records)
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_records = all_records[start_idx:end_idx]

        # --- 計算總工時 ---
        total_hours = sum(r.get('service_hours') or 0 for r in all_records)
        total_minutes = sum(r.get('service_minutes') or 0 for r in all_records)
        total_hours += total_minutes // 60
        total_minutes = total_minutes % 60

        cursor.close()
        conn.close()

        return render_template(
            'search.html',
            personal_records=current_page_records,
            nid=nid,
            name=name,
            total_hours=total_hours,
            total_minutes=total_minutes,
            date_start=date_start,
            date_end=date_end,
            page=page,
            total_pages=total_pages,
            total_records=total_records
        )

    # ----------- 編輯資料 -----------
    @app.route('/edit/<int:serial_no>', methods=['GET', 'POST'])
    def edit(serial_no):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            try:
                # ---------------------------------------------------
                # 1. [新增] 在更新之前，先抓取「舊的」身分證字號
                #    這樣我們才知道要連動修改哪些舊資料
                # ---------------------------------------------------
                cursor.execute("SELECT id_number FROM service_records WHERE serial_no = ?", (serial_no,))
                original_data = cursor.fetchone()
                old_id_number = original_data['id_number'] if original_data else None

                # ---------------------------------------------------
                # 2. 原本的資料處理邏輯 (保持不變)
                # ---------------------------------------------------
                fields = [
                    'name', 'id_number', 'service_start', 'service_end',
                    'service_item', 'service_content', 'service_hours', 'service_minutes',
                    'served_people_count', 'transport_fee', 'meal_fee',
                    'service_area', 'remarks', 'import_action', 'serial_number',
                    'foreign_service_count', 'domestic_service_count'
                ]

                values = []
                # 用來暫存新的姓名與身分證，給後面的批次更新使用
                new_name = request.form.get('name')
                new_id_number = request.form.get('id_number')

                # ✦ [新增] 檢查下班時間是否早於上班時間
                service_start_str = request.form.get('service_start')
                service_end_str = request.form.get('service_end')
                
                if service_start_str and service_end_str:
                    try:
                        service_start = datetime.strptime(service_start_str, '%Y-%m-%dT%H:%M')
                        service_end = datetime.strptime(service_end_str, '%Y-%m-%dT%H:%M')
                        
                        if service_end <= service_start:
                            cursor.close()
                            conn.close()
                            flash(f"❌ 下班時間不能早於或等於上班時間！\n上班：{service_start_str} | 下班：{service_end_str}", "error")
                            return redirect(url_for('admin_panel'))
                    except ValueError:
                        pass

                for f in fields:
                    v = request.form.get(f)
                    
                    # 處理日期時間格式
                    if f in ['service_start', 'service_end'] and v:
                        try:
                            v = datetime.strptime(v, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:00')
                        except ValueError:
                            v = None
                    
                    # 處理數值欄位
                    elif f in ["service_hours", "service_minutes", "served_people_count",
                              "transport_fee", "meal_fee",
                              "foreign_service_count", "domestic_service_count"]:
                        try:
                            v = int(v) if v and v.strip() else 0
                        except ValueError:
                            v = 0
                    
                    # 處理其他可為空的欄位
                    elif v is None or v.strip() == "":
                        v = None
                        
                    values.append(v)

                values.append(serial_no)

                # ---------------------------------------------------
                # 3. 執行原本的單筆更新 (針對 serial_no 更新所有欄位)
                # ---------------------------------------------------
                sql = """
                    UPDATE service_records
                    SET name=?, id_number=?, service_start=?, service_end=?,
                        service_item=?, service_content=?, service_hours=?, service_minutes=?,
                        served_people_count=?, transport_fee=?, meal_fee=?,
                        service_area=?, remarks=?, import_action=?, serial_number=?,
                        foreign_service_count=?, domestic_service_count=?
                    WHERE serial_no=?
                """
                cursor.execute(sql, tuple(values))

                # ---------------------------------------------------
                # 4. [新增] 批次連動更新：將該人員「所有」紀錄的姓名與身分證字號同步
                #    條件：如果舊的身分證字號存在，且有輸入新的資料
                # ---------------------------------------------------
                if old_id_number:
                    sync_sql = """
                        UPDATE service_records 
                        SET name = ?, id_number = ? 
                        WHERE id_number = ?
                    """
                    # 用 新的姓名、新的身分證，去更新所有 舊身分證 的資料
                    cursor.execute(sync_sql, (new_name, new_id_number, old_id_number))

                conn.commit()
                flash("✅ 資料已更新 (該人員所有紀錄已同步修改姓名與身分證)", "success")

            except Exception as e:
                conn.rollback() # 發生錯誤時回滾
                flash(f"❌ 錯誤：{e}", "error")
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('admin_panel'))

        # 讀取指定編號資料 (GET 請求)
        cursor.execute("SELECT * FROM service_records WHERE serial_no = ?", (serial_no,))
        record = cursor.fetchone()
        
        if record:
            # 將字串格式的日期轉換為 datetime 物件，以供 template 中的 strftime 使用
            for field in ['service_start', 'service_end']:
                if record.get(field) and isinstance(record[field], str):
                    try:
                        record[field] = datetime.strptime(record[field], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass
                        
        cursor.close()
        conn.close()
        return render_template('edit.html', record=record)

    # ----------- 新增記錄 -----------
    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_record():
        if request.method == 'POST':
            conn = get_connection()
            cursor = conn.cursor()

            try:
                fields = [
                    'name', 'id_number', 'service_start', 'service_end',
                    'service_item', 'service_content', 'service_hours', 'service_minutes',
                    'served_people_count', 'transport_fee', 'meal_fee',
                    'service_area', 'remarks', 'import_action', 'serial_number',
                    'foreign_service_count', 'domestic_service_count'
                ]

                values = []

                for f in fields:
                    v = request.form.get(f)
                    
                    # 處理日期時間格式
                    if f in ['service_start', 'service_end'] and v:
                        try:
                            v = datetime.strptime(v, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:00')
                        except ValueError:
                            v = None
                    
                    # 處理數值欄位
                    elif f in ["service_hours", "service_minutes", "served_people_count",
                              "transport_fee", "meal_fee",
                              "foreign_service_count", "domestic_service_count"]:
                        try:
                            v = int(v) if v and v.strip() else 0
                        except ValueError:
                            v = 0
                    
                    # 處理其他可為空的欄位
                    elif v is None or v.strip() == "":
                        v = None
                        
                    values.append(v)

                # 插入新紀錄
                sql = """
                    INSERT INTO service_records
                    (name, id_number, service_start, service_end,
                     service_item, service_content, service_hours, service_minutes,
                     served_people_count, transport_fee, meal_fee,
                     service_area, remarks, import_action, serial_number,
                     foreign_service_count, domestic_service_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql, tuple(values))
                conn.commit()
                flash("✅ 新紀錄已新增", "success")

            except Exception as e:
                conn.rollback()
                flash(f"❌ 錯誤：{e}", "error")
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('admin_panel'))

        # 新增頁面 (GET 請求) - 傳入預設值的 record 物件
        default_record = {
            'serial_no': None,
            'name': '',
            'id_number': '',
            'service_start': None,
            'service_end': None,
            'service_item': '0020',
            'service_content': '0028',
            'service_hours': 0,
            'service_minutes': 0,
            'served_people_count': 3,
            'transport_fee': 0,
            'meal_fee': 0,
            'service_area': 'D',
            'remarks': '',
            'import_action': 'A',
            'serial_number': '',
            'foreign_service_count': 0,
            'domestic_service_count': 0
        }
        return render_template('edit.html', record=default_record)

    # ----------- 刪除資料 -----------
    @app.route('/delete/<int:serial_no>')
    def delete(serial_no):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM service_records WHERE serial_no = ?", (serial_no,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('資料已刪除', 'info')
        return redirect(url_for('admin_panel'))