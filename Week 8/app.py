from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Book Model
class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'year': self.year,
            'available': self.available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Initialize database and sample data
def init_data():
    """Initialize database with sample data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if Book.query.count() == 0:
            # Add sample books
            sample_books = [
                Book(
                    title="Clean Code",
                    author="Robert C. Martin",
                    isbn="978-0132350884",
                    year=2008,
                    available=True
                ),
                Book(
                    title="Design Patterns",
                    author="Gang of Four",
                    isbn="978-0201633610",
                    year=1994,
                    available=True
                ),
                Book(
                    title="The Pragmatic Programmer",
                    author="Andrew Hunt, David Thomas",
                    isbn="978-0135957059",
                    year=2019,
                    available=False
                )
            ]
            
            db.session.add_all(sample_books)
            db.session.commit()
            print("✅ Database initialized with sample data")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }), 200


@app.route('/books', methods=['GET'])
def get_books():
    """Get all books with optional filtering"""
    # Query parameters for filtering
    available = request.args.get('available')
    author = request.args.get('author')
    
    # Build query
    query = Book.query
    
    if available is not None:
        is_available = available.lower() == 'true'
        query = query.filter_by(available=is_available)
    
    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))
    
    books = query.all()
    
    return jsonify({
        "success": True,
        "count": len(books),
        "books": [book.to_dict() for book in books]
    }), 200


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book by ID"""
    book = Book.query.get(book_id)
    
    if book is None:
        return jsonify({
            "success": False,
            "error": "Book not found"
        }), 404
    
    return jsonify({
        "success": True,
        "book": book.to_dict()
    }), 200


@app.route('/books', methods=['POST'])
def create_book():
    """Create a new book"""
    data = request.get_json()
    
    # Validation
    required_fields = ['title', 'author', 'isbn', 'year']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400
    
    # Check if ISBN already exists
    existing_book = Book.query.filter_by(isbn=data['isbn']).first()
    if existing_book:
        return jsonify({
            "success": False,
            "error": "Book with this ISBN already exists"
        }), 409
    
    # Create new book
    try:
        new_book = Book(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            year=int(data['year']),
            available=data.get('available', True)
        )
        
        db.session.add(new_book)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Book created successfully",
            "book": new_book.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to create book: {str(e)}"
        }), 500


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book"""
    book = Book.query.get(book_id)
    
    if book is None:
        return jsonify({
            "success": False,
            "error": "Book not found"
        }), 404
    
    data = request.get_json()
    
    try:
        # Update fields if provided
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'isbn' in data:
            # Check if new ISBN conflicts with another book
            existing = Book.query.filter_by(isbn=data['isbn']).first()
            if existing and existing.id != book_id:
                return jsonify({
                    "success": False,
                    "error": "ISBN already exists for another book"
                }), 409
            book.isbn = data['isbn']
        if 'year' in data:
            book.year = int(data['year'])
        if 'available' in data:
            book.available = data['available']
        
        book.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Book updated successfully",
            "book": book.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to update book: {str(e)}"
        }), 500


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    book = Book.query.get(book_id)
    
    if book is None:
        return jsonify({
            "success": False,
            "error": "Book not found"
        }), 404
    
    try:
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Book deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to delete book: {str(e)}"
        }), 500


@app.route('/books/reset', methods=['POST'])
def reset_data():
    """Reset data to initial state (useful for testing)"""
    try:
        # Delete all books
        Book.query.delete()
        db.session.commit()
        
        # Reinitialize with sample data
        init_data()
        
        return jsonify({
            "success": True,
            "message": "Data reset successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to reset data: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # Initialize database on first run
    init_data()
    app.run(debug=True, port=5000)
