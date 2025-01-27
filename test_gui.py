import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt  # برای دکمه‌های ماوس
from ui.main import MainWindow
import time

@pytest.fixture
def qt_app(qtbot):
    """ایجاد نمونه برنامه برای تست."""
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    qtbot.addWidget(window)
    return window


def test_login_page(qt_app, qtbot, mocker):
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"message": "Login successful"}

    qt_app.show_login_page()
    qtbot.keyClicks(qt_app.login_page.username_input, "testuser")
    qtbot.keyClicks(qt_app.login_page.password_input, "password123")
    qtbot.mouseClick(qt_app.login_page.login_button, Qt.LeftButton)

    assert qt_app.stack.currentWidget() == qt_app.chat_page
    mock_post.assert_called_with(
        "http://127.0.0.1:5000/login", json={"username": "testuser", "password": "password123"}
    )


def test_register_page(qt_app, qtbot, mocker):
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"message": "User registered successfully!"}

    qt_app.show_register_page()
    qtbot.keyClicks(qt_app.register_page.username_input, "newuser")
    qtbot.keyClicks(qt_app.register_page.email_input, "newuser@example.com")
    qtbot.keyClicks(qt_app.register_page.password_input, "password123")
    qtbot.mouseClick(qt_app.register_page.register_button, Qt.LeftButton)

    assert qt_app.stack.currentWidget() == qt_app.login_page
    mock_post.assert_called_with(
        "http://127.0.0.1:5000/register",
        json={"username": "newuser", "email": "newuser@example.com", "password": "password123"},
    )


def test_chat_page_send_message(qt_app, qtbot, mocker):
    """تست ارسال پیام در صفحه چت."""
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"message": "Message sent successfully"}

    qt_app.show_chat_page()
    qtbot.keyClicks(qt_app.chat_page.message_input, "Hello, World!")
    qtbot.mouseClick(qt_app.chat_page.send_button, Qt.LeftButton)

    assert "شما: Hello, World!" in qt_app.chat_page.message_box.toPlainText()
    mock_post.assert_called_with(
        "http://127.0.0.1:5000/send_message", json={"message": "Hello, World!"}
    )


def test_chat_page_create_group(qt_app, qtbot, mocker):
    """تست ایجاد گروه در صفحه چت."""
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"message": "Group created successfully"}

    qt_app.show_chat_page()
    qtbot.mouseClick(qt_app.chat_page.create_group_button, Qt.LeftButton)

    group_name = "Test Group"
    qtbot.keyClicks(qt_app.chat_page.message_input, group_name)
    qtbot.mouseClick(qt_app.chat_page.create_group_button, Qt.LeftButton)

    mock_post.assert_called_with("http://127.0.0.1:5000/create_group", json={"name": group_name})


def test_upload_page(qt_app, qtbot, mocker):
    qt_app.show_upload_page()
    print(f"دکمه آپلود مقداردهی شده است: {qt_app.upload_page.upload_button is not None}")
    print(f"دکمه آپلود قابل مشاهده است: {qt_app.upload_page.upload_button.isVisible()}")

    mock_post = mocker.patch("requests.post")
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"message": "File uploaded successfully"}

    qt_app.show_upload_page()
    time.sleep(2)  # زمان تأخیر برای نمایش صفحه آپلود
    qtbot.waitExposed(qt_app.upload_page.upload_button, timeout=15000)
    qtbot.mouseClick(qt_app.upload_page.upload_button, Qt.LeftButton)

    assert mock_post.called