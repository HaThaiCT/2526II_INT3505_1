from flask import Flask, jsonify, request, redirect
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/')
def home():
    return redirect('/apidocs')

# Mock data
users = [
    {"id": 1, "name": "Nguyen Van A", "email": "a@example.com"},
    {"id": 2, "name": "Tran Thi B", "email": "b@example.com"},
    {"id": 3, "name": "Le Van C", "email": "c@example.com"}
]

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    """
    List all users
    ---
    responses:
      200:
        description: A list of users
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              email:
                type: string
    """
    return jsonify(users)

@app.route('/api/v1/users/<int:id>', methods=['GET'])
def get_user(id):
    """
    Get one user by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The user ID
    responses:
      200:
        description: A single user
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
      404:
        description: User not found
    """
    user = next((user for user in users if user["id"] == id), None)
    if user:
        return jsonify(user)
    return jsonify({"message": "User not found"}), 404

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
          properties:
            name:
              type: string
            email:
              type: string
    responses:
      201:
        description: User created
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
    """
    data = request.get_json()
    new_id = max(user["id"] for user in users) + 1 if users else 1
    new_user = {
        "id": new_id,
        "name": data.get("name"),
        "email": data.get("email")
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/api/v1/users/<int:id>', methods=['PUT'])
def update_user(id):
    """
    Update a user
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The user ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
    responses:
      200:
        description: User updated
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
      404:
        description: User not found
    """
    user = next((user for user in users if user["id"] == id), None)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.get_json()
    user["name"] = data.get("name", user["name"])
    user["email"] = data.get("email", user["email"])
    return jsonify(user)

@app.route('/api/v1/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """
    Delete a user
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: The user ID
    responses:
      200:
        description: User deleted
      404:
        description: User not found
    """
    global users
    user = next((user for user in users if user["id"] == id), None)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    users = [u for u in users if u["id"] != id]
    return jsonify({"message": "User deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)