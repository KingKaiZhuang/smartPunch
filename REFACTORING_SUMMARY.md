# 📋 程式碼整理與功能完善總結

## ✅ 完成的重構工作

你的 `app.py` 已成功分解為**模組化結構**，並新增了**完整的使用者認證與註冊系統**！

## 📊 新的檔案組織

### 原始狀況
- ❌ 所有程式碼都在 `app.py` 中 (426 行)
- ❌ 只有基本登入功能
- ❌ 沒有使用者管理系統

### 現在的組織方式
- ✅ **app.py** → 只有 19 行（主程式進入點）
- ✅ **config.py** → Flask 配置 + bcrypt 密碼加密
- ✅ **user.py** → 使用者模型與認證
- ✅ **db.py** → 資料庫連線與操作
- ✅ **routes/** 資料夾
  - `auth_routes.py` → 登入/註冊/登出功能 ⭐ 已增強
  - `record_routes.py` → 服務記錄查詢、編輯、刪除
  - `export_routes.py` → Excel 匯出
  - `qrcode_routes.py` → QRCode 生成
- ✅ **MQTT 模組** → mqtt_sender.py, mqtt_server.py (IoT 支援)

---

## 📂 檔案對應表

| 原始功能 | 所在檔案 | 路由 |
|---------|---------|------|
| 登入頁面 | `routes/auth_routes.py` | `/login` |
| 使用者註冊 | `routes/auth_routes.py` | `/register` ⭐ 新增 |
| 登出 | `routes/auth_routes.py` | `/logout` |
| 後台主頁 | `routes/record_routes.py` | `/`, `/index` |
| 搜尋記錄 | `routes/record_routes.py` | `/search` ⭐ 新增 |
| 編輯資料 | `routes/record_routes.py` | `/edit/<serial_no>` |
| 刪除資料 | `routes/record_routes.py` | `/delete/<serial_no>` |
| 匯出 Excel | `routes/export_routes.py` | `/export_xlsx` |
| 生成 QRCode | `routes/qrcode_routes.py` | `/qrcode` |

---

## 🎯 優點

1. **更容易維護** - 每個文件都有明確的職責
2. **更容易測試** - 可獨立測試每個模組
3. **更容易擴展** - 新增功能只需新增路由檔案
4. **代碼重用** - 便於導入和共享功能
5. **更清晰** - 快速找到相關功能
6. **安全的認證** - 使用 bcrypt 加密密碼，無法被還原
7. **完整的權限管理** - 管理員授權制度，防止未授權註冊
8. **IoT 支援** - MQTT 模組支援物聯網通信

---

## 🚀 使用方法保持不變

程式運行方式完全相同：
```bash
python app.py
```

系統會自動在 `http://localhost:5000` 啟動。

### 第一次運行

如果這是第一次運行系統，請先執行遷移工具：
```bash
python "Test tool/migrate_passwords.py"
```

這會建立 `users` 資料表並創建預設管理員帳號。

所有路由和功能都保持不變。

---

## 💡 後續建議

如果要進一步改進，可以考慮：

1. **models/ 資料夾** - 放置資料庫模型
   ```
   models/
   ├── __init__.py
   ├── service_record.py
   └── user_model.py
   ```

2. **utils/ 資料夾** - 放置工具函數
   ```
   utils/
   ├── __init__.py
   ├── excel_helper.py
   ├── qrcode_helper.py
   └── validators.py
   ```

3. **tests/ 資料夾** - 放置測試檔案
   ```
   tests/
   ├── __init__.py
   ├── test_auth.py
   ├── test_records.py
   └── test_export.py
   ```

---

**完成時間**: 2025年11月14日 ✨

# 👤 使用者註冊系統使用指南

## 🎯 系統特色

✅ **雙重驗證** - 註冊需要管理員授權
✅ **權限分級** - 管理員 vs 普通使用者
✅ **密碼加密** - 使用 bcrypt 安全加密
✅ **完整驗證** - 表單驗證 + 資料庫驗證

## 📦 安裝步驟

### 1. 安裝必要套件
```bash
pip install flask-bcrypt
```

### 2. 執行資料庫遷移
```bash
python migrate_passwords.py
```

這會自動：
- 建立 `users` 資料表（含 `role` 欄位）
- 建立預設管理員帳號 `admin` (密碼: `0000`)

### 3. 資料表結構
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🚀 使用流程

### 情境 1: 第一次設定系統

1. **執行遷移工具**
   ```bash
   python migrate_passwords.py
   ```

2. **啟動系統**
   ```bash
   python app.py
   ```

3. **使用預設管理員登入**
   - 帳號: `admin`
   - 密碼: `0000`
   - 權限: 管理員

### 情境 2: 註冊新使用者

1. **訪問註冊頁面**
   - 點擊登入頁面的「註冊新使用者」連結
   - 或直接訪問 `http://localhost:5000/register`

2. **填寫新使用者資訊**
   - 帳號: 4-20個字元，只能包含英文、數字、底線
   - 密碼: 至少4個字元
   - 確認密碼: 必須與密碼一致
   - 權限: 選擇「普通使用者」或「管理員」

3. **管理員授權驗證**
   - 輸入現有管理員的帳號
   - 輸入管理員的密碼
   - ⚠️ 必須是「管理員」權限的帳號才能授權

4. **完成註冊**
   - 系統驗證通過後建立新使用者
   - 自動跳轉到登入頁面

## 🔐 權限說明

### 管理員 (admin)
- ✅ 完整系統權限
- ✅ 可以授權註冊新使用者
- ✅ 可以註冊新的管理員
- ✅ 可以註冊普通使用者

### 普通使用者 (user)
- ✅ 可以登入系統
- ✅ 可以使用基本功能
- ❌ **不能**授權註冊新使用者

## 📋 註冊驗證規則

### 表單驗證
1. ✅ 所有欄位必填
2. ✅ 帳號格式：4-20字元，英文數字底線
3. ✅ 密碼長度：至少4個字元
4. ✅ 密碼一致性：兩次輸入必須相同

### 管理員驗證
1. ✅ 管理員帳號必須存在
2. ✅ 管理員密碼必須正確
3. ✅ 授權者必須是管理員身份

### 資料庫驗證
1. ✅ 使用者名稱不能重複

## 🎨 頁面路由

| 路由 | 功能 | 方法 |
|------|------|------|
| `/login` | 登入頁面 | GET, POST |
| `/register` | 註冊頁面 | GET, POST |
| `/logout` | 登出 | GET |

## 💡 使用範例

### 範例 1: 註冊一個普通使用者

**步驟：**
1. 訪問 `/register`
2. 填寫資料：
   - 帳號: `john_doe`
   - 密碼: `pass1234`
   - 確認密碼: `pass1234`
   - 權限: 選擇「普通使用者」
   - 管理員帳號: `admin`
   - 管理員密碼: `0000`
3. 提交表單
4. 成功後跳轉到登入頁面

### 範例 2: 註冊一個新的管理員

**步驟：**
1. 訪問 `/register`
2. 填寫資料：
   - 帳號: `manager`
   - 密碼: `secure123`
   - 確認密碼: `secure123`
   - 權限: 選擇「管理員」⭐
   - 管理員帳號: `admin`
   - 管理員密碼: `0000`
3. 提交表單
4. 現在 `manager` 也可以授權註冊新使用者了

## 🛡️ 安全特性

1. **密碼加密**
   - 使用 bcrypt 單向加密
   - 每次加密都使用隨機 salt
   - 密碼無法被還原

2. **雙重驗證**
   - 註冊必須有管理員授權
   - 防止未授權的帳號註冊

3. **權限控制**
   - 只有管理員可以授權註冊
   - 普通使用者無法授權

4. **輸入驗證**
   - 前端 HTML5 驗證
   - 後端 Python 驗證
   - 資料庫唯一性約束

## ⚠️ 注意事項

### 1. 保管好管理員帳號
- 管理員帳號密碼一旦遺失，需要手動重設
- 建議定期更改管理員密碼

### 2. 謹慎授予管理員權限
- 管理員擁有完整系統權限
- 只授予信任的人員

### 3. 密碼安全
- 建議使用強密碼（混合大小寫、數字、符號）
- 不要使用常見密碼
- 定期更換密碼

### 4. 帳號管理
- 及時移除不再使用的帳號
- 定期審查使用者清單

## 🔧 常見問題

### Q1: 忘記管理員密碼怎麼辦？

**解決方法：**
```python
python migrate_passwords.py
# 選擇 y 重設 admin 密碼
```

### Q2: 如何查看所有使用者？

**解決方法：**
```sql
SELECT id, username, role, created_at FROM users;
```

### Q3: 如何手動將使用者升級為管理員？

**解決方法：**
```sql
UPDATE users SET role = 'admin' WHERE username = '使用者名稱';
```

### Q4: 註冊時顯示「管理員帳號或密碼錯誤」

**原因：**
- 輸入的管理員帳號不存在
- 管理員密碼錯誤
- 授權者不是管理員身份

**解決方法：**
- 確認管理員帳號正確
- 確認管理員密碼正確
- 確認授權者是 `admin` 權限

### Q5: 使用者名稱已被使用

**原因：** 資料庫中已有相同的使用者名稱

**解決方法：** 使用不同的使用者名稱

## 📊 系統流程圖

```
[使用者訪問註冊頁面]
        ↓
[填寫新使用者資訊]
        ↓
[填寫管理員授權資訊]
        ↓
[提交表單]
        ↓
[驗證所有欄位完整性] ──❌→ [顯示錯誤訊息]
        ↓ ✅
[驗證密碼一致性] ──❌→ [顯示錯誤訊息]
        ↓ ✅
[驗證管理員身份] ──❌→ [顯示錯誤訊息]
        ↓ ✅
[檢查使用者名稱是否重複] ──❌→ [顯示錯誤訊息]
        ↓ ✅
[建立新使用者（密碼加密）]
        ↓
[跳轉到登入頁面]
```

## 🎉 完成

現在你的系統已經具備完整的註冊功能了！

---

**更新日期**: 2025年11月16日
**版本**: 3.0 (註冊系統版)