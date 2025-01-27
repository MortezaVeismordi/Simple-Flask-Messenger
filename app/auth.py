import logging
import jwt
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from app.models import User
from app import db

# ایجاد بلوپرینت برای احراز هویت
auth_bp = Blueprint('auth', __name__)

# تنظیمات لاگ
logger = logging.getLogger('AuthLogger')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# ----------------- مسیر ثبت‌نام -----------------
@auth_bp.route('/register', methods=['POST'])
def register():
    """ثبت‌نام کاربر جدید"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # بررسی فیلدهای ورودی
        if not username or not email or not password:
            logger.warning("Registration failed: Missing required fields.")
            return jsonify({"error": "All fields are required"}), 400

        # بررسی وجود نام کاربری یا ایمیل تکراری
        if User.query.filter_by(username=username).first():
            logger.warning(f"Registration failed: Username '{username}' already exists.")
            return jsonify({"error": "Username already exists"}), 400

        if User.query.filter_by(email=email).first():
            logger.warning(f"Registration failed: Email '{email}' already exists.")
            return jsonify({"error": "Email already exists"}), 400

        # هش کردن رمز عبور و ذخیره در پایگاه داده
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"User '{username}' registered successfully.")
        return jsonify({"message": "User registered successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during registration: {str(e)}")
        return jsonify({"error": "An error occurred during registration"}), 500

# ----------------- مسیر ورود -----------------
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json if request.content_type == 'application/json' else request.form
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            payload = {
                "user_id": user.id,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=current_app.config['JWT_EXPIRATION_DELTA'])
            }
            token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

            return jsonify({"message": "Login successful", "token": token}), 200

        return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        current_app.logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": "An error occurred during login"}), 500

# ----------------- بررسی اعتبار توکن -----------------
@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """بررسی اعتبار توکن JWT"""
    try:
        token = request.json.get('token')
        if not token:
            logger.warning("Token verification failed: Missing token.")
            return jsonify({"error": "Token is required"}), 400

        # بررسی صحت توکن
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        user_id = payload.get('user_id')

        logger.info(f"Token verified successfully for user_id {user_id}.")
        return jsonify({"message": "Token is valid", "user_id": user_id}), 200

    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token has expired.")
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        logger.warning("Token verification failed: Invalid token.")
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        logger.error(f"Error during token verification: {str(e)}")
        return jsonify({"error": "An error occurred during token verification"}), 500
