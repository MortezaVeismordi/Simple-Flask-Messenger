from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  # ارجاع به شیء `db` از فایل `__init__.py`

# مدل کاربران
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # ارتباط با پیام‌ها
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

    # ارتباط با عضویت در گروه‌ها
    groups = db.relationship('Group', secondary='group_members', backref=db.backref('members', lazy='dynamic'))

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """هش کردن رمز عبور"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """بررسی رمز عبور هش‌شده"""
        return check_password_hash(self.password_hash, password)

    def save(self):
        """ذخیره یک کاربر در دیتابیس"""
        try:
            db.session.add(self)
            db.session.commit()
            print(f"User '{self.username}' saved successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving user '{self.username}': {e}")
            raise

# مدل پیام‌ها
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Message {self.id} from {self.sender_id}>"

    def save(self):
        """ذخیره یک پیام در دیتابیس"""
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Message '{self.id}' saved successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving message '{self.id}': {e}")
            raise

# مدل گروه‌ها
class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # ارتباط با پیام‌ها
    messages = db.relationship('Message', backref='group', lazy=True)

    def __repr__(self):
        return f"<Group {self.name}>"

    def save(self):
        """ذخیره یک گروه در دیتابیس"""
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Group '{self.name}' saved successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving group '{self.name}': {e}")
            raise

# مدل اعضای گروه‌ها
class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<GroupMember group={self.group_id}, user={self.user_id}>"

    def save(self):
        """ذخیره یک عضو گروه در دیتابیس"""
        try:
            db.session.add(self)
            db.session.commit()
            print(f"GroupMember (group_id={self.group_id}, user_id={self.user_id}) saved successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving GroupMember (group_id={self.group_id}, user_id={self.user_id}): {e}")
            raise

# مدل فایل‌های آپلودشده
class FileUpload(db.Model):
    __tablename__ = 'file_uploads'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<FileUpload {self.filename}>"

    def save(self):
        """ذخیره فایل آپلودشده در دیتابیس"""
        try:
            db.session.add(self)
            db.session.commit()
            print(f"FileUpload '{self.filename}' saved successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving FileUpload '{self.filename}': {e}")
            raise
