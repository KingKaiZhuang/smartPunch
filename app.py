"""
QR Code 服務記錄系統 - 主應用程式
"""
from config import create_app
from routes.auth_routes import register_auth_routes
from routes.record_routes import register_record_routes
from routes.export_routes import register_export_routes
from routes.qrcode_routes import register_qrcode_routes

# 建立 Flask 應用程式
app = create_app()

# 註冊各個功能模組的路由
register_auth_routes(app)
register_record_routes(app)
register_export_routes(app)
register_qrcode_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)