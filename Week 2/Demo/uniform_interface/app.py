"""
1. UNIFORM INTERFACE - Giao diện thống nhất
Sử dụng HTTP methods chuẩn: GET, POST, PUT, DELETE
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

# Dữ liệu mẫu
books = [
    {"id": 1, "title": "Python", "author": "John"},
    {"id": 2, "title": "Flask", "author": "Jane"}
]

# GET - Lấy tất cả
@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify(books)

# GET - Lấy 1 sách
@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    book = next((b for b in books if b['id'] == id), None)
    return jsonify(book) if book else (jsonify({"error": "Not found"}), 404)

# POST - Tạo mới
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.json
    new_book = {
        "id": len(books) + 1,
        "title": data['title'],
        "author": data['author']
    }
    books.append(new_book)
    return jsonify(new_book), 201

# PUT - Cập nhật
@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = next((b for b in books if b['id'] == id), None)
    if not book:
        return jsonify({"error": "Not found"}), 404
    
    data = request.json
    book['title'] = data.get('title', book['title'])
    book['author'] = data.get('author', book['author'])
    return jsonify(book)

# DELETE - Xóa
@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    global books
    books = [b for b in books if b['id'] != id]
    return jsonify({"message": "Deleted"})

if __name__ == '__main__':
    print("=" * 50)
    print("UNIFORM INTERFACE - Port 5001")
    print("GET    /api/books")
    print("POST   /api/books")
    print("PUT    /api/books/1")
    print("DELETE /api/books/1")
    print("=" * 50)
    app.run(port=5001)
