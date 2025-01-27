import os
import pytest
from app import create_app, db
from app.models import User, Group, Message, FileUpload

@pytest.fixture
def test_client():
    """ایجاد یک کلاینت تست برای اپلیکیشن Flask"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # پایگاه داده در حافظه
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test_secret_key'  # کلید JWT برای تست
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads_test')  # پوشه تست برای آپلود فایل‌ها

    # ایجاد پوشه آپلود تست
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()

            # حذف پوشه تست
            for file in os.listdir(app.config['UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
            os.rmdir(app.config['UPLOAD_FOLDER'])

def get_jwt_token(test_client):
    """ثبت‌نام و ورود کاربر برای دریافت توکن JWT"""
    response = test_client.post('/auth/register', json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 201, f"Failed to register user: {response.json}"

    response = test_client.post('/auth/login', json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200, f"Login failed with status: {response.status_code}, {response.json}"
    return response.json['token']

def test_register_user(test_client):
    """تست ثبت‌نام کاربر"""
    response = test_client.post('/auth/register', json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 201, f"Failed to register user: {response.json}"
    assert response.json["message"] == "User registered successfully!"

def test_login_user(test_client):
    """تست ورود کاربر"""
    test_client.post('/auth/register', json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    })
    response = test_client.post('/auth/login', json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200, f"Login failed: {response.json}"
    assert "token" in response.json

def test_protected_route_no_token(test_client):
    """تست دسترسی به مسیر محافظت‌شده بدون توکن"""
    response = test_client.post('/api/messages', json={
        "content": "Hello, this is a test message!"
    })
    assert response.status_code == 401, f"Unexpected response: {response.json}"
    assert response.json["error"] == "Token is missing!"

def test_protected_route_invalid_token(test_client):
    """تست دسترسی به مسیر محافظت‌شده با توکن نامعتبر"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_client.post('/api/messages', headers=headers, json={
        "content": "Hello, this is a test message!"
    })
    assert response.status_code == 401, f"Unexpected response: {response.json}"
    assert response.json["error"] == "Invalid token!"

def test_send_message(test_client):
    """تست ارسال پیام با توکن معتبر"""
    token = get_jwt_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.post('/api/messages', headers=headers, json={
        "content": "Hello, this is a test message!"
    })
    assert response.status_code == 201, f"Message sending failed: {response.json}"
    assert response.json["message"] == "Message sent successfully!"

def test_create_group(test_client):
    """تست ایجاد گروه با توکن معتبر"""
    token = get_jwt_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.post('/api/groups', headers=headers, json={
        "name": "Test Group"
    })
    assert response.status_code == 201, f"Group creation failed: {response.json}"
    assert response.json["message"] == "Group created successfully!"

def test_add_member_to_group(test_client):
    """تست افزودن عضو به گروه"""
    token = get_jwt_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}

    # ایجاد گروه
    test_client.post('/api/groups', headers=headers, json={"name": "Test Group"})

    # ثبت‌نام کاربر جدید
    test_client.post('/auth/register', json={
        "username": "member",
        "email": "member@example.com",
        "password": "password123"
    })

    # افزودن عضو به گروه
    response = test_client.post('/api/groups/1/add_member', headers=headers, json={
        "user_id": 2
    })
    assert response.status_code == 201, f"Failed to add member: {response.json}"
    assert response.json["message"] == "Member added to group successfully!"

def test_upload_file(test_client):
    """تست آپلود فایل با توکن معتبر"""
    token = get_jwt_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}

    # آپلود فایل
    with open('test_image.png', 'wb') as f:
        f.write(b'test file content')
    with open('test_image.png', 'rb') as img:
        response = test_client.post('/api/upload', headers=headers, data={'file': img})

    assert response.status_code == 201, f"File upload failed: {response.json}"
    assert "File uploaded successfully!" in response.json["message"]

def test_delete_file(test_client):
    """تست حذف فایل با توکن معتبر"""
    token = get_jwt_token(test_client)
    headers = {"Authorization": f"Bearer {token}"}

    # آپلود فایل
    with open('test_image.png', 'wb') as f:
        f.write(b'test file content')
    with open('test_image.png', 'rb') as img:
        test_client.post('/api/upload', headers=headers, data={'file': img})

    # حذف فایل
    response = test_client.delete('/api/delete/test_image.png', headers=headers)
    assert response.status_code == 200, f"File deletion failed: {response.json}"
    assert response.json["message"] == "File deleted successfully!"
