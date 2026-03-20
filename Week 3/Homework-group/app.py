from flask import Flask, jsonify, request

app = Flask(__name__)

users = [
    {"id": 1, "name": "Nguyễn Văn A", "email": "a@test.com", "age": 25},
    {"id": 2, "name": "Trần Thị B", "email": "b@test.com", "age": 30}
]

orders = [
    {"id": 1, "user_id": 1, "product": "Laptop", "quantity": 1, "total": 1000},
    {"id": 2, "user_id": 2, "product": "Mouse", "quantity": 2, "total": 40}
]

next_user_id = 3
next_order_id = 3

@app.route('/')
def home():
    return jsonify({
        "Users API": {
            "GET /api/v1/users": "List all",
            "GET /api/v1/users/{id}": "Get one",
            "POST /api/v1/users": "Create",
            "PUT /api/v1/users/{id}": "Update",
            "DELETE /api/v1/users/{id}": "Delete"
        },
        "Orders API": {
            "GET /api/v1/orders": "List all",
            "GET /api/v1/orders/{id}": "Get one",
            "POST /api/v1/orders": "Create",
            "PUT /api/v1/orders/{id}": "Update",
            "DELETE /api/v1/orders/{id}": "Delete"
        }
    })

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    global next_user_id
    data = request.json
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Missing name or email"}), 400
    
    new_user = {
        "id": next_user_id,
        "name": data['name'],
        "email": data['email'],
        "age": data.get('age', 0)
    }
    users.append(new_user)
    next_user_id += 1
    
    return jsonify(new_user), 201

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    if data:
        user['name'] = data.get('name', user['name'])
        user['email'] = data.get('email', user['email'])
        user['age'] = data.get('age', user['age'])
    
    return jsonify(user), 200

@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    users.remove(user)
    return jsonify({"message": "User deleted"}), 200

@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    return jsonify(orders), 200

@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200

@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    global next_order_id
    data = request.json
    
    if not data or 'user_id' not in data or 'product' not in data:
        return jsonify({"error": "Missing user_id or product"}), 400
    
    new_order = {
        "id": next_order_id,
        "user_id": data['user_id'],
        "product": data['product'],
        "quantity": data.get('quantity', 1),
        "total": data.get('total', 0)
    }
    orders.append(new_order)
    next_order_id += 1
    
    return jsonify(new_order), 201

@app.route('/api/v1/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    data = request.json
    if data:
        order['user_id'] = data.get('user_id', order['user_id'])
        order['product'] = data.get('product', order['product'])
        order['quantity'] = data.get('quantity', order['quantity'])
        order['total'] = data.get('total', order['total'])
    
    return jsonify(order), 200

@app.route('/api/v1/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    orders.remove(order)
    return jsonify({"message": "Order deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
