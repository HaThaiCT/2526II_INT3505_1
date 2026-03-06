"""
REST API Principle: Uniform Interface
Mô tả: Sử dụng các phương thức HTTP chuẩn (GET, POST, PUT, DELETE) 
       và URI có cấu trúc nhất quán
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# Dữ liệu mẫu (giả lập database)
books = [
    {"id": 1, "title": "Python Programming", "author": "John Doe", "year": 2020},
    {"id": 2, "title": "Flask Web Development", "author": "Jane Smith", "year": 2021},
    {"id": 3, "title": "REST API Design", "author": "Bob Wilson", "year": 2022}
]

# Root endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Uniform Interface API Demo",
        "description": "Sử dụng HTTP methods chuẩn và URI thống nhất",
        "endpoints": {
            "GET /api/books": "Lấy tất cả sách",
            "GET /api/books/:id": "Lấy sách theo ID",
            "POST /api/books": "Tạo sách mới",
            "PUT /api/books/:id": "Cập nhật sách",
            "DELETE /api/books/:id": "Xóa sách"
        }
    }), 200

# GET - Lấy tất cả sách
@app.route('/api/books', methods=['GET'])
def get_books():
    """Lấy danh sách tất cả sách"""
    return jsonify({
        "success": True,
        "count": len(books),
        "data": books
    }), 200

# GET - Lấy một cuốn sách theo ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Lấy thông tin chi tiết 1 cuốn sách"""
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify({
            "success": True,
            "data": book
        }), 200
    return jsonify({
        "success": False,
        "error": "Book not found"
    }), 404

# POST - Tạo sách mới
@app.route('/api/books', methods=['POST'])
def create_book():
    """Tạo sách mới"""
    data = request.get_json()
    
    # Validation
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({
            "success": False,
            "error": "Missing required fields: title and author"
        }), 400
    
    new_book = {
        "id": max([b['id'] for b in books]) + 1 if books else 1,
        "title": data.get('title'),
        "author": data.get('author'),
        "year": data.get('year', 2024)
    }
    books.append(new_book)
    
    return jsonify({
        "success": True,
        "message": "Book created successfully",
        "data": new_book
    }), 201

# PUT - Cập nhật sách
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Cập nhật thông tin sách"""
    book = next((b for b in books if b['id'] == book_id), None)
    
    if not book:
        return jsonify({
            "success": False,
            "error": "Book not found"
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "error": "No data provided"
        }), 400
    
    # Cập nhật các trường
    book['title'] = data.get('title', book['title'])
    book['author'] = data.get('author', book['author'])
    book['year'] = data.get('year', book['year'])
    
    return jsonify({
        "success": True,
        "message": "Book updated successfully",
        "data": book
    }), 200

# DELETE - Xóa sách
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Xóa sách"""
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    
    if not book:
        return jsonify({
            "success": False,
            "error": "Book not found"
        }), 404
    
    books = [b for b in books if b['id'] != book_id]
    
    return jsonify({
        "success": True,
        "message": "Book deleted successfully",
        "data": book
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("UNIFORM INTERFACE API DEMO")
    print("=" * 60)
    print("Server running on: http://localhost:5001")
    print("\nEndpoints:")
    print("  GET    http://localhost:5001/api/books")
    print("  GET    http://localhost:5001/api/books/1")
    print("  POST   http://localhost:5001/api/books")
    print("  PUT    http://localhost:5001/api/books/1")
    print("  DELETE http://localhost:5001/api/books/1")
    print("=" * 60)
    app.run(debug=True, port=5001)
