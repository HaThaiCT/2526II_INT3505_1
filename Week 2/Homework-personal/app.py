from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

users = [
    {"id": 1, "username": "admin", "email": "admin@test.com", "password": "123456"},
    {"id": 2, "username": "user1", "email": "user1@test.com", "password": "123456"}
]
next_id = 3
tokens = {}
rate_limit = {}

@app.route('/')
def home():
    return jsonify({
        "endpoints": [
            "POST /login - Đăng nhập",
            "GET /users - Lấy danh sách user",
            "POST /users - Tạo user mới",
            "PUT /users/<id>/email - Cập nhật email",
            "DELETE /users/<id> - Xóa user"
        ]
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Thiếu username hoặc password"}), 400
    
    user = next((u for u in users if u['username'] == data['username']), None)
    if not user or user['password'] != data['password']:
        return jsonify({"error": "Sai username hoặc password"}), 401
    
    token = f"TOKEN_{user['username']}_{datetime.now().timestamp()}"
    tokens[token] = user['username']
    
    return jsonify({"token": token, "user": {k:v for k,v in user.items() if k != 'password'}}), 200

@app.route('/users', methods=['GET'])
def get_users():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token or token not in tokens:
        return jsonify({"error": "Token không hợp lệ"}), 401
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if page < 1 or limit < 1:
        return jsonify({"error": "page và limit phải > 0"}), 400
    
    start = (page - 1) * limit
    end = start + limit
    data = [{"id": u['id'], "username": u['username'], "email": u['email']} for u in users[start:end]]
    
    return jsonify({
        "data": data,
        "page": page,
        "limit": limit,
        "total": len(users)
    }), 200

@app.route('/users', methods=['POST'])
def create_user():
    global next_id
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token or token not in tokens:
        return jsonify({"error": "Token không hợp lệ"}), 401
    
    data = request.json
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({"error": "Thiếu thông tin bắt buộc"}), 400
    
    if any(u['username'] == data['username'] for u in users):
        return jsonify({"error": "Username đã tồn tại"}), 400
    
    if '@' not in data['email']:
        return jsonify({"error": "Email không hợp lệ"}), 400
    
    new_user = {
        "id": next_id,
        "username": data['username'],
        "email": data['email'],
        "password": data['password']
    }
    users.append(new_user)
    next_id += 1
    
    return jsonify({k:v for k,v in new_user.items() if k != 'password'}), 201

@app.route('/users/<int:user_id>/email', methods=['PUT'])
def update_email(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token or token not in tokens:
        return jsonify({"error": "Token không hợp lệ"}), 401
    
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "Không tìm thấy user"}), 404
    
    data = request.json
    if not data or 'email' not in data:
        return jsonify({"error": "Thiếu email"}), 400
    
    if '@' not in data['email']:
        return jsonify({"error": "Email không hợp lệ"}), 400
    
    user['email'] = data['email']
    return jsonify({k:v for k,v in user.items() if k != 'password'}), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token or token not in tokens:
        return jsonify({"error": "Token không hợp lệ"}), 401
    
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "Không tìm thấy user"}), 404
    
    users.remove(user)
    return jsonify({"message": "Đã xóa user"}), 200

@app.errorhandler(429)
def rate_limit_error(e):
    return jsonify({"error": "Quá nhiều request"}), 429

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Lỗi server"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
