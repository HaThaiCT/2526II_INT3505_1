from flask import Flask, jsonify, request
from flasgger import Flasgger
import json

app = Flask(__name__)


with open('openapi.yaml', 'r', encoding='utf-8') as f:
    openapi_spec = f.read()


swag = Flasgger(app, spec=json.loads(json.dumps({
    'swagger': '3.0.0',
})))


books = [
    {'id': 1, 'title': 'Python Basics', 'author': 'John Doe', 'year': 2020, 'isbn': '123-456'},
    {'id': 2, 'title': 'REST API Design', 'author': 'Jane Smith', 'year': 2021, 'isbn': '789-012'},
]

next_id = 3

@app.route('/books', methods=['GET'])
def get_books():
    """Get all books"""
    return jsonify(books), 200

@app.route('/books', methods=['POST'])
def create_book():
    """Create a new book"""
    global next_id
    data = request.get_json()
    
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_book = {
        'id': next_id,
        'title': data.get('title'),
        'author': data.get('author'),
        'year': data.get('year'),
        'isbn': data.get('isbn')
    }
    books.append(new_book)
    next_id += 1
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a book by ID"""
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify(book), 200
    return jsonify({'error': 'Book not found'}), 404

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update a book"""
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    data = request.get_json()
    book.update({k: v for k, v in data.items() if v is not None})
    return jsonify(book), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        books = [b for b in books if b['id'] != book_id]
        return '', 204
    return jsonify({'error': 'Book not found'}), 404

if __name__ == '__main__':
    print('Open http://localhost:5000/apidocs')
    app.run(debug=True, host='0.0.0.0', port=5000)
