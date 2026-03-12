"""
REST API Principle: Stateless
Mô tả: Mỗi request chứa tất cả thông tin cần thiết để xử lý,
       server không lưu trữ trạng thái của client
"""

from flask import Flask, jsonify, request
from functools import wraps
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

# Secret key cho JWT (trong thực tế nên lưu trong config/env)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Giả lập database users
users_db = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # Trong thực tế phải hash password
        "name": "Administrator",
        "role": "admin"
    },
    "user1": {
        "username": "user1", 
        "password": "user123",
        "name": "Nguyen Van A",
        "role": "user"
    }
}

# Database sản phẩm
products_db = [
    {"id": 1, "name": "Laptop", "price": 1000},
    {"id": 2, "name": "Mouse", "price": 20},
    {"id": 3, "name": "Keyboard", "price": 50}
]

# LOGIN - Tạo token
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = users.get(username)
    if user and user['password'] == password:
        # Giả lập token (thực tế dùng JWT)
        token = f"TOKEN_{username}"
        return jsonify({"token": token, "name": user['name']})
    
    return jsonify({"error": "Invalid credentials"}), 401

# GET Profile - Cần token trong header
@app.route('/api/profile', methods=['GET'])
def get_profile():
    # Lấy token từ header
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing token"}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    # Parse token (đơn giản hóa)
    if token.startswith('TOKEN_'):
        username = token.replace('TOKEN_', '')
        user = users.get(username)
        if user:
            return jsonify({"username": username, "name": user['name']})
    
    return jsonify({"error": "Invalid token"}), 401

# Tính toán - Stateless (tất cả data trong request)
@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    a = data.get('a', 0)
    b = data.get('b', 0)
    operation = data.get('operation', 'add')
    
    if operation == 'add':
        result = a + b
    elif operation == 'subtract':
        result = a - b
    else:
        result = a * b
    
    return jsonify({"a": a, "b": b, "result": result})

if __name__ == '__main__':
    print("=" * 50)
    print("STATELESS - Port 5002")
    print("POST /api/login")
    print("GET  /api/profile (with token)")
    print("POST /api/calculate")
    print("=" * 50)
    print("Test: admin/123 or user1/456")
    app.run(port=5002)
