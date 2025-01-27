import os
import app
import logging
from flask import Blueprint, Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from app.models import User, Message, Group, GroupMember, FileUpload
from app.utils import token_required, allowed_file
from app import db, socketio
from datetime import datetime, timedelta
import jwt

routes_bp = Blueprint('routes', __name__)

# تنظیمات لاگ
def configure_logging():
    logger = logging.getLogger('RoutesLogger')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = configure_logging()

@routes_bp.route('/')
def index():
    return render_template('index.html')

@routes_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            token = jwt.encode(
                {"user_id": user.id, "exp": datetime.utcnow() + timedelta(seconds=current_app.config.get('JWT_EXPIRATION_DELTA', 3600))},
                current_app.config['JWT_SECRET_KEY'],
                algorithm="HS256"
            )
            return jsonify({"token": token}), 200

        logger.warning("Login failed: Invalid credentials.")
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": "An error occurred during login. Please try again later."}), 500

@routes_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({"error": "All fields are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"User '{username}' registered successfully.")
        return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during registration: {str(e)}")
        return jsonify({"error": "An error occurred during registration. Please try again later."}), 500

@routes_bp.route('/api/groups/<group_id>/join', methods=['POST'])
@token_required
def join_group(current_user, group_id):
    # بررسی اینکه گروه وجود دارد یا خیر
    group = Group.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({"error": "Group not found"}), 404

    # بررسی اینکه کاربر قبلاً عضو گروه است یا خیر
    if current_user in group.members:
        return jsonify({"message": "You are already a member of this group"}), 200

    # افزودن کاربر به گروه
    group.members.append(current_user)
    group.save()

    return jsonify({"message": f"User '{current_user.username}' joined the group '{group.name}'"}), 200

@routes_bp.route('/api/upload', methods=['POST'])
@token_required
def upload(user_id):
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.abspath(os.path.join(upload_folder, filename))

        # ذخیره فایل
        file.save(file_path)

        # ثبت در پایگاه داده
        new_file = FileUpload(user_id=user_id, filename=filename, filepath=file_path)
        db.session.add(new_file)
        db.session.commit()

        return jsonify({"message": "File uploaded successfully!"}), 201

    return jsonify({"error": "Invalid file or no file selected!"}), 400

@routes_bp.route('/api/messages', methods=['GET'])
@token_required
def get_messages(user_id):
    try:
        messages = Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).all()
        if not messages:
            return jsonify({"message": "No messages found."}), 200

        result = [
            {"id": msg.id, "content": msg.content, "timestamp": msg.timestamp.isoformat()}
            for msg in messages
        ]
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error fetching messages for user {user_id}: {str(e)}")
        return jsonify({"error": "An error occurred while fetching messages"}), 500

@routes_bp.route('/send_message', methods=['POST'])
@token_required
def send_message(user_id):
    try:
        data = request.json
        receiver_id = data.get('receiver_id')
        group_id = data.get('group_id')
        content = data.get('content')

        if not content:
            return jsonify({"error": "Message content is required"}), 400

        new_message = Message(sender_id=user_id, receiver_id=receiver_id, group_id=group_id, content=content)
        db.session.add(new_message)
        db.session.commit()

        socketio.emit('new_message', {
            "sender_id": user_id,
            "receiver_id": receiver_id,
            "group_id": group_id,
            "content": content,
            "timestamp": new_message.timestamp.isoformat()
        })

        return jsonify({"message": "Message sent successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({"error": "An error occurred while sending the message"}), 500


@routes_bp.route('/api/delete/<filename>', methods=['DELETE'])
@token_required
def delete_file(user_id, filename):
    try:
        file = FileUpload.query.filter_by(filename=filename, user_id=user_id).first()

        if not file:
            logger.warning(f"File '{filename}' not found or user {user_id} does not own it.")
            return jsonify({"error": "File not found or you do not have permission to delete it"}), 404

        try:
            os.remove(file.filepath)
        except FileNotFoundError:
            logger.warning(f"File '{file.filepath}' already deleted or does not exist.")

        db.session.delete(file)
        db.session.commit()

        logger.info(f"File '{filename}' deleted successfully by user {user_id}.")
        return jsonify({"message": "File deleted successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting file '{filename}': {str(e)}")
        return jsonify({"error": "An error occurred while deleting the file"}), 500

@routes_bp.route('/api/groups', methods=['POST'])
@token_required
def create_group(user_id):
    try:
        data = request.json
        name = data.get('name')
        if not name:
            logger.warning("Group creation failed: Missing group name.")
            return jsonify({"error": "Group name is required"}), 400

        new_group = Group(name=name)
        db.session.add(new_group)
        db.session.commit()

        logger.info(f"Group '{name}' created successfully by user {user_id}.")
        return jsonify({"message": "Group created successfully!", "group_id": new_group.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating group: {str(e)}")
        return jsonify({"error": "An error occurred while creating the group"}), 500

@routes_bp.route('/api/groups/<int:group_id>/add_member', methods=['POST'])
@token_required
def add_member_to_group(user_id, group_id):
    try:
        data = request.json
        member_id = data.get('user_id')
        if not member_id:
            logger.warning(f"Failed to add member to group {group_id}: Missing user_id.")
            return jsonify({"error": "User ID is required"}), 400

        group = db.session.get(Group, group_id)
        if not group:
            logger.warning(f"Failed to add member: Group {group_id} does not exist.")
            return jsonify({"error": "Group does not exist"}), 404

        new_member = GroupMember(group_id=group_id, user_id=member_id)
        db.session.add(new_member)
        db.session.commit()

        logger.info(f"User {member_id} added to group {group_id} successfully.")
        return jsonify({"message": "Member added to group successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding member to group {group_id}: {str(e)}")
        return jsonify({"error": "An error occurred while adding member to the group"}), 500
