from flask import Flask, jsonify, request
from flasgger import Flasgger, swag_from
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Flasgger for Swagger UI
swagger = Flasgger(app, config={
    "headers": [],
    "specs": [
        {
            "endpoint": 'openapi',
            "route": '/openapi.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs",
})

# In-memory database for books
books_db = {
    "1": {
        "id": "1",
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "publishedYear": 2008,
        "genre": "Software Engineering"
    },
    "2": {
        "id": "2",
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt, David Thomas",
        "publishedYear": 1999,
        "genre": "Programming"
    },
    "3": {
        "id": "3",
        "title": "Design Patterns",
        "author": "Gang of Four",
        "publishedYear": 1994,
        "genre": "Software Design"
    }
}

next_id = 4


@app.route('/books', methods=['GET'])
def get_books():
    """
    List all books
    ---
    tags:
      - Books
    summary: List all books
    responses:
      200:
        description: A list of books
        schema:
          type: array
          items:
            $ref: '#/definitions/Book'
    """
    return jsonify(list(books_db.values())), 200


@app.route('/books', methods=['POST'])
def create_book():
    """
    Create a new book
    ---
    tags:
      - Books
    summary: Create a new book
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/NewBook'
    responses:
      201:
        description: Book created successfully
        schema:
          $ref: '#/definitions/Book'
      400:
        description: Invalid input
    """
    global next_id
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ['title', 'author', 'publishedYear']):
        return jsonify({"error": "Missing required fields"}), 400
    
    book = {
        "id": str(next_id),
        "title": data['title'],
        "author": data['author'],
        "publishedYear": data['publishedYear'],
        "genre": data.get('genre', '')
    }
    
    books_db[str(next_id)] = book
    next_id += 1
    
    return jsonify(book), 201


@app.route('/books/<id>', methods=['GET'])
def get_book(id):
    """
    Get a book by ID
    ---
    tags:
      - Books
    summary: Get a book by ID
    parameters:
      - in: path
        name: id
        required: true
        type: string
        description: The unique identifier of the book
    responses:
      200:
        description: Book details
        schema:
          $ref: '#/definitions/Book'
      404:
        description: Book not found
    """
    if id not in books_db:
        return jsonify({"error": "Book not found"}), 404
    
    return jsonify(books_db[id]), 200


@app.route('/books/<id>', methods=['PUT'])
def update_book(id):
    """
    Update a book
    ---
    tags:
      - Books
    summary: Update a book
    parameters:
      - in: path
        name: id
        required: true
        type: string
        description: The unique identifier of the book
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/NewBook'
    responses:
      200:
        description: Book updated successfully
        schema:
          $ref: '#/definitions/Book'
      404:
        description: Book not found
      400:
        description: Invalid input
    """
    if id not in books_db:
        return jsonify({"error": "Book not found"}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    
    book = books_db[id]
    book['title'] = data.get('title', book['title'])
    book['author'] = data.get('author', book['author'])
    book['publishedYear'] = data.get('publishedYear', book['publishedYear'])
    book['genre'] = data.get('genre', book.get('genre', ''))
    
    return jsonify(book), 200


@app.route('/books/<id>', methods=['DELETE'])
def delete_book(id):
    """
    Delete a book
    ---
    tags:
      - Books
    summary: Delete a book
    parameters:
      - in: path
        name: id
        required: true
        type: string
        description: The unique identifier of the book
    responses:
      204:
        description: Book deleted successfully
      404:
        description: Book not found
    """
    if id not in books_db:
        return jsonify({"error": "Book not found"}), 404
    
    del books_db[id]
    return '', 204


@app.route('/api/docs', methods=['GET'])
def swagger_ui():
    """Swagger UI endpoint"""
    return swagger.render()


@app.route('/', methods=['GET'])
def home():
    """API home page"""
    return jsonify({
        "message": "Simple Books Management API",
        "version": "1.0.0",
        "docs_url": "http://localhost:5000/api/docs",
        "endpoints": {
            "books": {
                "GET": "Get all books",
                "POST": "Create a new book"
            },
            "books/{id}": {
                "GET": "Get a book by ID",
                "PUT": "Update a book",
                "DELETE": "Delete a book"
            }
        }
    }), 200


# Definition for Swagger UI
@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    from flask import send_from_directory
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
