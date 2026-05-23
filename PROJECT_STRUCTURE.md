# QR Code 服務記錄系統 - 專案結構

## 📁 檔案架構

```
QR code/
│
├── app.py                      # 主應用程式入口
├── config.py                   # Flask 應用配置
├── db.py                       # SQLiteCloud 資料庫連線和基本操作
├── user.py                     # 使用者認證模組
├── qr_scanner.py              # QR code 掃描功能
│
├── routes/                     # 路由模組（按功能分類）
│   ├── __init__.py            # 套件初始化
│   ├── auth_routes.py         # 登入/註冊/登出路由
│   ├── record_routes.py       # 服務記錄查詢、編輯、刪除
│   ├── export_routes.py       # Excel 匯出功能
│   └── qrcode_routes.py       # QRCode 生成路由
│
├── templates/                  # HTML 模板 (Apple Minimalist Style)
│   ├── index.html            # 後台主頁
│   ├── login.html            # 登入頁面
│   ├── register.html         # 註冊頁面
│   ├── edit.html             # 編輯記錄頁面
│   ├── QRcode.html           # QRCode 生成頁面
│   └── search.html           # 搜尋結果頁面
│
├── static/                     # 靜態資源
│   ├── style.css             # 主樣式表 (極簡蘋果風)
│   ├── search.css            # 搜尋頁面樣式
│   ├── search.js             # 搜尋功能腳本
│   └── scroll-fix.js         # 滾動修復腳本
│
├── utils/                      # 實用工具腳本
│   ├── init_sqlitecloud.py   # SQLiteCloud 初始化腳本
│   ├── fix_admin.py          # 修復管理員帳號工具
│   ├── migrate_passwords.py  # 資料庫遷移工具
│   ├── xls_to_xlsx.py        # 格式轉換工具
│   └── xlsx_to_xls.py        # 格式轉換工具
│
└── __pycache__/               # Python 快取檔案
```

## 🚀 模組說明

### 核心模組

- **app.py** - 應用程式的主進入點 (19 行)，負責應用配置和路由註冊
- **config.py** - Flask 應用配置，包含 Flask-Login 初始化和 bcrypt 密碼加密
- **db.py** - SQLiteCloud 資料庫連線管理和基本操作
- **user.py** - 使用者認證和權限管理系統
- **qr_scanner.py** - QR code 掃描功能
- **mqtt_sender.py** - MQTT 訊息傳送模組
- **mqtt_server.py** - MQTT 伺服器模組

### 路由模組 (routes/)

#### 1. **auth_routes.py** - 認證模組
   - `/login` - 登入頁面 (GET, POST)
   - `/register` - 使用者註冊 (GET, POST)
   - `/logout` - 登出功能 (GET)

#### 2. **record_routes.py** - 服務記錄管理
   - `/` 及 `/index` - 後台主頁，顯示所有服務記錄 (GET, POST)
   - `/search` - 搜尋服務記錄 (GET, POST)
   - `/edit/<serial_no>` - 編輯服務記錄 (GET, POST)
   - `/delete/<serial_no>` - 刪除服務記錄 (GET)
   
#### 3. **export_routes.py** - 資料匯出
   - `/export_xlsx` - 匯出搜尋結果到 Excel (GET, POST)
   
#### 4. **qrcode_routes.py** - QRCode 管理
   - `/qrcode` - 生成 QRCode (GET, POST)

## 📦 依賴套件

```
Flask
Flask-Login
sqlitecloud
openpyxl
qrcode
Pillow
flask-bcrypt
paho-mqtt
```

## 🔑 主要特性

✅ **模組化設計** - 程式碼按功能清晰分類
✅ **雲端資料庫** - 採用 SQLiteCloud，輕量且支援雲端同步
✅ **極簡美學 UI** - 全面套用 Apple Minimalist Style (蘋果極簡風)，視覺留白、藍色藥丸按鈕與現代黑體
✅ **雙重認證系統** - 登入驗證 + 註冊授權
✅ **密碼加密** - 使用 bcrypt 安全加密
✅ **權限管理** - 管理員 vs 普通使用者分級
✅ **資料庫操作** - 完整的 CRUD 功能
✅ **Excel 匯出** - 支援搜尋結果批量匯出
✅ **QRCode 生成** - 動態生成人員 QRCode
✅ **分頁功能** - 大量資料的頁面顯示優化
✅ **MQTT 支援** - IoT 訊息傳送功能

## 🚀 如何執行

```bash
python app.py
```

預設運行於 `http://localhost:5000`

## 📝 登入憑證

預設管理員帳號：
- 帳號：`admin`
- 密碼：`0000`
- 權限：管理員 (admin)

> 💡 新使用者註冊需要現有管理員授權

---

**開發日期**: 2026年5月21日
**版本**: 3.0 (雲端資料庫 SQLiteCloud 升級 & 蘋果極簡風 UI 改版)
