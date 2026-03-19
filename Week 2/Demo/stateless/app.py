from datetime import datetime, timedelta, timezone
from functools import wraps
import uuid

import jwt
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_EXPIRES_HOURS'] = 1

# In-memory sample data (reset every time server restarts)
users_data = [
    {
        'public_id': 'sample-admin-id',
        'name': 'Administrator',
        'email': 'admin@example.com',
        'role': 'admin',
        'password': generate_password_hash('admin123'),
    },
    {
        'public_id': 'sample-user-id',
        'name': 'Sample User',
        'email': 'user1@example.com',
        'role': 'user',
        'password': generate_password_hash('user123'),
    },
]

products_data = [
    {'id': 1, 'name': 'Laptop', 'price': 1000},
    {'id': 2, 'name': 'Mouse', 'price': 20},
    {'id': 3, 'name': 'Keyboard', 'price': 50},
]


def find_user_by_email(email):
    for user in users_data:
        if user['email'] == email:
            return user
    return None


def find_user_by_public_id(public_id):
    for user in users_data:
        if user['public_id'] == public_id:
            return user
    return None


def create_access_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        'public_id': user['public_id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role'],
        'iat': now,
        'exp': now + timedelta(hours=app.config['JWT_EXPIRES_HOURS']),
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])


def get_bearer_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ', 1)[1].strip()
    return token or None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_bearer_token()

        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
            current_user = find_user_by_public_id(data['public_id'])
            if current_user is None:
                return jsonify({'success': False, 'error': 'Token is invalid'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Token is invalid'}), 401

        return f(current_user, data, *args, **kwargs)

    return decorated


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'success': True, 'message': 'Stateless API is running'})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip()
    password = str(data.get('password', ''))

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400

    user = find_user_by_email(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

    token = create_access_token(user)
    return jsonify(
        {
            'success': True,
            'message': 'Login successful',
            'token_type': 'Bearer',
            'token': token,
            'expires_in': 3600,
        }
    )


@app.route('/api/signup', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip()
    password = str(data.get('password', ''))

    if not name or not email or not password:
        return jsonify({'success': False, 'error': 'Name, email and password are required'}), 400

    existing_user = find_user_by_email(email)
    if existing_user:
        return jsonify({'success': False, 'error': 'User already exists. Please login'}), 409

    new_user = {
        'public_id': str(uuid.uuid4()),
        'name': name,
        'email': email,
        'role': 'user',
        'password': generate_password_hash(password),
    }
    users_data.append(new_user)
    return jsonify({'success': True, 'message': 'User registered successfully'}), 201


@app.route('/api/profile', methods=['GET'])
@token_required
def profile(current_user, token_payload):
    return jsonify(
        {
            'success': True,
            'data': {
                'public_id': current_user['public_id'],
                'name': token_payload.get('name', current_user['name']),
                'email': token_payload.get('email', current_user['email']),
                'role': token_payload.get('role', current_user['role']),
            },
        }
    )


@app.route('/api/products', methods=['GET'])
@token_required
def products(current_user, token_payload):
    return jsonify(
        {
            'success': True,
            'requested_by': token_payload.get('email', current_user['email']),
            'data': products_data,
        }
    )


@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json(silent=True) or {}
    num1 = data.get('num1')
    num2 = data.get('num2')
    operation = str(data.get('operation', 'add')).strip().lower()

    if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
        return jsonify({'success': False, 'error': 'num1 and num2 must be numbers'}), 400

    if operation == 'add':
        result = num1 + num2
    elif operation == 'subtract':
        result = num1 - num2
    elif operation == 'multiply':
        result = num1 * num2
    elif operation == 'divide':
        if num2 == 0:
            return jsonify({'success': False, 'error': 'Cannot divide by zero'}), 400
        result = num1 / num2
    else:
        return jsonify({'success': False, 'error': 'Unsupported operation'}), 400

    return jsonify(
        {
            'success': True,
            'input': {'num1': num1, 'num2': num2, 'operation': operation},
            'result': result,
        }
    )


if __name__ == '__main__':
    print('=' * 50)
    print('STATELESS API - Port 5002')
    print('POST /api/signup')
    print('POST /api/login')
    print('GET  /api/profile (Bearer token)')
    print('GET  /api/products (Bearer token)')
    print('POST /api/calculate')
    print('=' * 50)
    app.run(port=5002, debug=True)