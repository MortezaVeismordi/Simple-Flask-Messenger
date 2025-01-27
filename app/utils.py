import jwt
import logging
from flask import request, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta, timezone

# تنظیمات لاگ
logger = logging.getLogger('UtilsLogger')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def token_required(f):
    """
    یک دکوریتور برای بررسی توکن JWT و محافظت از مسیرها.
    اگر توکن معتبر نباشد، خطای مناسب بازگردانده می‌شود.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            logger.warning("Access denied: Token is missing.")
            return jsonify({"error": "Token is missing!"}), 401

        # حذف کلمه "Bearer " از ابتدای توکن
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            # بررسی توکن JWT
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            logger.warning("Access denied: Token has expired.")
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            logger.warning("Access denied: Invalid token.")
            return jsonify({"error": "Invalid token!"}), 401
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {str(e)}")
            return jsonify({"error": "An error occurred while validating the token"}), 500

        # اضافه کردن user_id به پارامترهای مسیر
        kwargs['user_id'] = payload['user_id']
        return f(*args, **kwargs)

    return decorated

def generate_token(user_id):
    """
    تولید یک توکن JWT برای کاربر.
    :param user_id: شناسه کاربر برای ذخیره در توکن
    :return: توکن JWT
    """
    try:
        expiration_delta = current_app.config.get('JWT_EXPIRATION_DELTA', 3600)  # مقدار پیش‌فرض 3600 ثانیه (1 ساعت)
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expiration_delta)
        }
        token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")
        logger.info(f"Token generated successfully for user_id {user_id}.")
        return token
    except Exception as e:
        logger.error(f"Error generating token for user_id {user_id}: {str(e)}")
        return None

def allowed_file(filename):
    """
    بررسی می‌کند که فایل دارای نوع مجاز است یا خیر.
    :param filename: نام فایل برای بررسی
    :return: True اگر فایل مجاز باشد، False در غیر این صورت
    """
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    is_allowed = extension in allowed_extensions
    if not is_allowed:
        logger.warning(f"File with extension '{extension}' is not allowed.")
    return is_allowed
