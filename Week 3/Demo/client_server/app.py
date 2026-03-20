"""
REST API Principle: Client-Server
Mô tả: Tách biệt client và server, cho phép chúng phát triển độc lập
       Server cung cấp API, client tiêu thụ API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Cho phép cross-origin requests từ frontend

# =========================
# SERVER SIDE (Backend API)
# =========================

# Database giả lập (server-side data storage)
tasks_db = [
    {"id": 1, "title": "Học Flask", "description": "Tìm hiểu về Flask framework", "completed": False, "priority": "high"},
    {"id": 2, "title": "Học REST API", "description": "Nắm vững các nguyên lý REST", "completed": True, "priority": "high"},
    {"id": 3, "title": "Làm bài tập", "description": "Hoàn thành bài tập tuần 2", "completed": False, "priority": "medium"}
]

categories_db = ["Work", "Study", "Personal", "Shopping"]

# Root endpoint - API documentation
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Client-Server Architecture Demo",
        "description": "Server cung cấp API, Client độc lập với Server",
        "server_responsibilities": [
            "Quản lý dữ liệu (database)",
            "Xử lý business logic",
            "Validate dữ liệu",
            "Cung cấp API endpoints"
        ],
        "client_responsibilities": [
            "Hiển thị UI",
            "Xử lý user interaction",
            "Gọi API để lấy/cập nhật data",
            "Render data từ API"
        ],
        "api_endpoints": {
            "GET /api/tasks": "Lấy danh sách tasks",
            "GET /api/tasks/:id": "Lấy task theo ID",
            "POST /api/tasks": "Tạo task mới",
            "PUT /api/tasks/:id": "Cập nhật task",
            "DELETE /api/tasks/:id": "Xóa task",
            "GET /api/categories": "Lấy danh sách categories",
            "GET /api/stats": "Thống kê tasks"
        }
    }), 200

# GET - Lấy tất cả tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """
    Server trả về dữ liệu dạng JSON
    Client tự quyết định cách hiển thị
    """
    # Query parameters (optional filtering)
    completed = request.args.get('completed')
    priority = request.args.get('priority')
    
    filtered_tasks = tasks_db
    
    if completed is not None:
        is_completed = completed.lower() == 'true'
        filtered_tasks = [t for t in filtered_tasks if t['completed'] == is_completed]
    
    if priority:
        filtered_tasks = [t for t in filtered_tasks if t['priority'] == priority]
    
    return jsonify({
        "success": True,
        "count": len(filtered_tasks),
        "data": filtered_tasks
    }), 200

# GET - Lấy task theo ID
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Server xử lý logic tìm kiếm"""
    task = next((t for t in tasks_db if t['id'] == task_id), None)
    
    if task:
        return jsonify({
            "success": True,
            "data": task
        }), 200
    
    return jsonify({
        "success": False,
        "error": "Task not found"
    }), 404

# POST - Tạo task mới
@app.route('/api/tasks', methods=['POST'])
def create_task():
    """
    Server xử lý business logic và validation
    Client chỉ gửi data và nhận kết quả
    """
    data = request.get_json()
    
    # Validation (server-side)
    if not data or not data.get('title'):
        return jsonify({
            "success": False,
            "error": "Title is required"
        }), 400
    
    # Business logic (server-side)
    new_task = {
        "id": max([t['id'] for t in tasks_db]) + 1 if tasks_db else 1,
        "title": data.get('title'),
        "description": data.get('description', ''),
        "completed": False,
        "priority": data.get('priority', 'medium')
    }
    
    tasks_db.append(new_task)
    
    return jsonify({
        "success": True,
        "message": "Task created successfully",
        "data": new_task
    }), 201

# PUT - Cập nhật task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Server quản lý state của dữ liệu"""
    task = next((t for t in tasks_db if t['id'] == task_id), None)
    
    if not task:
        return jsonify({
            "success": False,
            "error": "Task not found"
        }), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "No data provided"
        }), 400
    
    # Update fields
    task['title'] = data.get('title', task['title'])
    task['description'] = data.get('description', task['description'])
    task['completed'] = data.get('completed', task['completed'])
    task['priority'] = data.get('priority', task['priority'])
    
    return jsonify({
        "success": True,
        "message": "Task updated successfully",
        "data": task
    }), 200

# DELETE - Xóa task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Server xử lý việc xóa dữ liệu"""
    global tasks_db
    task = next((t for t in tasks_db if t['id'] == task_id), None)
    
    if not task:
        return jsonify({
            "success": False,
            "error": "Task not found"
        }), 404
    
    tasks_db = [t for t in tasks_db if t['id'] != task_id]
    
    return jsonify({
        "success": True,
        "message": "Task deleted successfully"
    }), 200

# GET - Categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Server cung cấp master data"""
    return jsonify({
        "success": True,
        "data": categories_db
    }), 200

# GET - Statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Server xử lý tính toán phức tạp
    Client chỉ hiển thị kết quả
    """
    total = len(tasks_db)
    completed = len([t for t in tasks_db if t['completed']])
    pending = total - completed
    
    priority_count = {
        "high": len([t for t in tasks_db if t['priority'] == 'high']),
        "medium": len([t for t in tasks_db if t['priority'] == 'medium']),
        "low": len([t for t in tasks_db if t['priority'] == 'low'])
    }
    
    return jsonify({
        "success": True,
        "data": {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_rate": round((completed / total * 100) if total > 0 else 0, 2),
            "priority_breakdown": priority_count
        }
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("CLIENT-SERVER ARCHITECTURE DEMO")
    print("=" * 60)
    print("Server (Backend API) running on: http://localhost:5004")
    print("\nServer responsibilities:")
    print("  ✓ Quản lý database (tasks, categories)")
    print("  ✓ Xử lý business logic")
    print("  ✓ Validate dữ liệu")
    print("  ✓ Cung cấp JSON API")
    print("\nClient có thể là:")
    print("  - Web app (HTML/JavaScript/React/Vue)")
    print("  - Mobile app (iOS/Android)")
    print("  - Desktop app")
    print("  - Postman (API testing tool)")
    print("\nAPI Endpoints:")
    print("  GET    http://localhost:5004/api/tasks")
    print("  GET    http://localhost:5004/api/tasks/:id")
    print("  POST   http://localhost:5004/api/tasks")
    print("  PUT    http://localhost:5004/api/tasks/:id")
    print("  DELETE http://localhost:5004/api/tasks/:id")
    print("  GET    http://localhost:5004/api/categories")
    print("  GET    http://localhost:5004/api/stats")
    print("=" * 60)
    app.run(debug=True, port=5004)
