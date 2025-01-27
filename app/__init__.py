import os
import logging
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# مقداردهی اولیه SQLAlchemy و SocketIO
db = SQLAlchemy()
socketio = SocketIO(logger=True, engineio_logger=True)
migrate = Migrate()

def create_app():
    """ایجاد و پیکربندی اپلیکیشن Flask"""
    # ایجاد اپلیکیشن Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    # تنظیمات پایگاه داده
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # مسیر پایگاه داده
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # تنظیمات JWT
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # کلید مخفی
    app.config['JWT_EXPIRATION_DELTA'] = 3600  # زمان انقضای توکن (به ثانیه)

    # تنظیمات آپلود فایل‌ها
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # حداکثر اندازه فایل (16MB)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # اطمینان از وجود پوشه آپلود

    # مقداردهی اولیه ماژول‌ها
    db.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)

    # ایجاد جداول پایگاه داده
    with app.app_context():
        db.create_all()

    # تنظیمات لاگ
    setup_logging(app)

    # ثبت بلوپرینت‌ها
    from .auth import auth_bp
    from .routes import routes_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(routes_bp, url_prefix="/")

    # مسیر برای دسترسی به فایل‌های آپلود شده
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """نمایش فایل آپلود شده"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # پیام اولیه برای تایید اجرای برنامه
    app.logger.info("Flask application initialized successfully.")

    return app

def setup_logging(app):
    """تنظیمات لاگ برای اپلیکیشن"""
    # سطح لاگینگ
    log_level = logging.DEBUG

    # قالب‌بندی لاگ‌ها
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # ایجاد هندلر کنسول
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # ایجاد هندلر فایل برای ذخیره لاگ‌ها در فایل
    log_file = os.path.join(os.getcwd(), 'logs', 'app.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # حذف هندلرهای پیش‌فرض و اضافه کردن هندلرهای جدید
    app.logger.handlers = []
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)

    # تنظیم سطح لاگ
    app.logger.setLevel(log_level)

    # لاگ اولیه برای تأیید
    app.logger.info("Logging is configured.")


# تست و اجرای اپلیکیشن
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        app.logger.info("Testing logs inside __init__.py")
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
