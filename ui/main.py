import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QVBoxLayout,
    QHBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QMessageBox, QFileDialog, QListWidget,QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("پیام رسان")
        self.setGeometry(100, 100, 900, 700)

        # Load CSS Stylesheet
        self.load_stylesheet()

        # Stacked Widget to manage pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.login_page = LoginPage(self)
        self.register_page = RegisterPage(self)
        self.chat_page = ChatPage(self)
        self.create_group_page = CreateGroupPage(self)

        # Add pages to stack
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        self.stack.addWidget(self.chat_page)
        self.stack.addWidget(self.create_group_page)

        # Show the login page initially
        self.show_login_page()

    def load_stylesheet(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            css_path = os.path.join(base_path, "styles.css")
            print(f"در حال جستجو برای فایل CSS در مسیر: {css_path}")
            with open(css_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
            print("فایل styles.css با موفقیت بارگذاری شد.")
        except FileNotFoundError:
            print(f"فایل styles.css پیدا نشد. مسیر بررسی‌شده: {css_path}")
        except UnicodeDecodeError as e:
            print(f"خطای کدگذاری فایل CSS: {e}")

    def show_login_page(self):
        self.stack.setCurrentWidget(self.login_page)

    def show_register_page(self):
        self.stack.setCurrentWidget(self.register_page)

    def show_chat_page(self):
        self.stack.setCurrentWidget(self.chat_page)

    def show_create_group_page(self):
        self.stack.setCurrentWidget(self.create_group_page)


class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری")
        self.username_input.setObjectName("usernameInput")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("passwordInput")

        self.login_button = QPushButton("ورود")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("ثبت‌نام")
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.main_window.show_register_page)

        layout.addWidget(QLabel("ورود به پیام‌رسان"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "خطا", "نام کاربری و رمز عبور را وارد کنید!")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:5000/login",
                json={"username": username, "password": password}
            )

            if response.status_code == 200:
                token = response.json().get('token')
                if not token:
                    QMessageBox.critical(self, "خطا", "توکن احراز هویت دریافت نشد.")
                    return

                self.main_window.token = token
                QMessageBox.information(self, "موفق", "ورود موفقیت‌آمیز!")
                self.main_window.show_chat_page()
            else:
                QMessageBox.critical(self, "خطا", "نام کاربری یا رمز عبور اشتباه است.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "خطا", f"خطای ارتباط با سرور: {str(e)}")


class RegisterPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری")
        self.username_input.setObjectName("usernameInput")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ایمیل")
        self.email_input.setObjectName("emailInput")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("passwordInput")

        self.register_button = QPushButton("ثبت‌نام")
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.register)

        self.back_button = QPushButton("بازگشت به ورود")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.main_window.show_login_page)

        layout.addWidget(QLabel("ثبت‌نام در پیام‌رسان"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if not username or not email or not password:
            QMessageBox.warning(self, "خطا", "تمامی فیلدها را پر کنید!")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:5000/register",
                json={"username": username, "email": email, "password": password}
            )
            if response.status_code == 201:
                QMessageBox.information(self, "موفق", "ثبت‌نام موفقیت‌آمیز بود! اکنون وارد شوید.")
                self.main_window.show_login_page()
            else:
                QMessageBox.critical(self, "خطا", "ثبت‌نام انجام نشد. لطفاً دوباره تلاش کنید.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "خطا", f"خطای ارتباط با سرور: {str(e)}")


class ChatPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        self.group_list = QListWidget()
        self.group_list.setFixedHeight(200)

        self.message_list = QListWidget()
        self.message_list.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc; border-radius: 10px;")

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("پیام خود را بنویسید...")

        self.send_button = QPushButton("ارسال")
        self.send_button.clicked.connect(self.send_message)

        self.upload_button = QPushButton("آپلود فایل")
        self.upload_button.clicked.connect(self.upload_file)

        self.create_group_button = QPushButton("ایجاد گروه")
        self.create_group_button.clicked.connect(self.main_window.show_create_group_page)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        layout.addWidget(self.group_list)
        layout.addWidget(self.message_list)
        layout.addLayout(input_layout)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.create_group_button)

        self.setLayout(layout)

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.add_message(f"شما: {message}", "blue")
            self.message_input.clear()

            try:
                headers = {"Authorization": f"Bearer {self.main_window.token}"}
                response = requests.post(
                    "http://127.0.0.1:5000/send_message",
                    json={"content": message},
                    headers=headers
                )
                if response.status_code != 201:
                    self.add_message("ارسال پیام ناموفق بود.", "red")
            except requests.exceptions.RequestException as e:
                self.add_message(f"خطای ارتباط با سرور: {str(e)}", "red")

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل برای آپلود")
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    headers = {"Authorization": f"Bearer {self.main_window.token}"}
                    response = requests.post(
                        "http://127.0.0.1:5000/upload",
                        files={"file": (file_path.split("/")[-1], f)},
                        headers=headers
                    )
                if response.status_code == 200:
                    file_name = response.json().get("file_name", "فایل")
                    self.add_message(f"فایل آپلود شد: {file_name}", "green")
                else:
                    self.add_message("آپلود فایل ناموفق بود.", "red")
            except requests.exceptions.RequestException as e:
                self.add_message(f"خطای ارتباط با سرور: {str(e)}", "red")

    def add_message(self, content, color="black"):
        item = QListWidgetItem(content)
        item.setForeground(QtGui.QColor(color))
        self.message_list.addItem(item)


class CreateGroupPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        title = QLabel("ایجاد گروه جدید")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")

        self.group_name_input = QLineEdit()
        self.group_name_input.setPlaceholderText("نام گروه")

        self.create_button = QPushButton("ایجاد گروه")
        self.create_button.clicked.connect(self.create_group)

        self.join_group_button = QPushButton("عضویت در گروه")
        self.join_group_button.clicked.connect(self.join_group)

        self.back_button = QPushButton("بازگشت")
        self.back_button.clicked.connect(self.main_window.show_chat_page)

        layout.addWidget(title)
        layout.addWidget(self.group_name_input)
        layout.addWidget(self.create_button)
        layout.addWidget(self.join_group_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def create_group(self):
        group_name = self.group_name_input.text()
        if not group_name:
            QMessageBox.warning(self, "خطا", "نام گروه نمی‌تواند خالی باشد!")
            return
        try:
            headers = {"Authorization": f"Bearer {self.main_window.token}"}
            response = requests.post("http://127.0.0.1:5000/api/groups", json={"name": group_name}, headers=headers)
            if response.status_code == 201:
                QMessageBox.information(self, "موفق", f"گروه '{group_name}' با موفقیت ایجاد شد!")
                self.main_window.show_chat_page()
            else:
                QMessageBox.warning(self, "خطا", "ایجاد گروه ناموفق بود.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "خطا", f"خطای ارتباط با سرور: {str(e)}")

    def join_group(self):
        group_name = self.group_name_input.text()
        if not group_name:
            QMessageBox.warning(self, "خطا", "نام گروه نمی‌تواند خالی باشد!")
            return
        try:
            headers = {"Authorization": f"Bearer {self.main_window.token}"}
            response = requests.post(f"http://127.0.0.1:5000/api/groups/{group_name}/join", headers=headers)
            if response.status_code == 200:
                QMessageBox.information(self, "موفق", f"شما با موفقیت به گروه '{group_name}' پیوستید!")
                self.main_window.show_chat_page()
            else:
                QMessageBox.warning(self, "خطا", "عضویت در گروه ناموفق بود.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "خطا", f"خطای ارتباط با سرور: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
