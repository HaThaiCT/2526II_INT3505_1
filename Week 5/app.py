from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
# Sử dụng SQLite in-memory để demo, hoặc đổi thành tên file 'sqlite:///library.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 1. DATA MODELS
# ==========================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    joined_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relationship to Loan
    loans = db.relationship('Loan', backref='user', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    published_year = db.Column(db.Integer, nullable=True)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    
    loans = db.relationship('Loan', backref='book', lazy=True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='borrowed') # 'borrowed', 'returned'

# ==========================================
# 2. ENDPOINTS CHO TÌM KIẾM VÀ PHÂN TRANG (BOOKS)
# ==========================================

@app.route('/books', methods=['GET'])
def get_books():
    """Lấy danh sách sách, hỗ trợ tìm kiếm (?q=...) và phân trang (?page=1&limit=10)"""
    
    # Nhận query parameters
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    # Base query
    query = Book.query
    
    # 2.1. Tìm kiếm (Search)
    if search_query:
        # Tìm kiếm theo tên sách hoặc tên tác giả, case-insensitive (SQLite hỗ trợ ILIKE qua filter)
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Book.title.like(search_term),
                Book.author.like(search_term)
            )
        )
        
    # Sắp xếp mặc định
    query = query.order_by(Book.id.asc())

    # 2.2. Phân trang (Pagination)
    # Flask-SQLAlchemy có sẵn .paginate() cực kỳ tiện lợi
    paginated_books = query.paginate(page=page, per_page=limit, error_out=False)
    
    # Chuẩn bị Response payload
    items = []
    for b in paginated_books.items:
        items.append({
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "published_year": b.published_year,
            "available_copies": b.available_copies,
            "total_copies": b.total_copies
        })
        
    return jsonify({
        "data": items,
        "pagination": {
            "total_items": paginated_books.total,
            "total_pages":paginated_books.pages,
            "current_page": paginated_books.page,
            "limit": paginated_books.per_page,
            "has_next": paginated_books.has_next,
            "has_prev": paginated_books.has_prev
        }
    })

# Đăng ký sách mới
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(
        title=data['title'],
        author=data['author'],
        published_year=data.get('published_year'),
        total_copies=data.get('total_copies', 1),
        available_copies=data.get('total_copies', 1)
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully", "id": new_book.id}), 201


# ==========================================
# 3. ENDPOINTS THEO RESOURCE TREE (NESTED ROUTING)
# ==========================================

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully", "id": new_user.id}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

# GET /users/{id}/loans - Lấy danh sách lịch sử mượn sách của CỤ THỂ 1 người dùng
@app.route('/users/<int:user_id>/loans', methods=['GET'])
def get_user_loans(user_id):
    """Lấy danh sách sách đang mượn và đã trả của người dùng"""
    user = User.query.get_or_404(user_id)
    
    # Lọc parameter phụ nếu cần, ví dụ: ?status=borrowed
    status_filter = request.args.get('status')
    
    query = Loan.query.filter_by(user_id=user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    loans = query.all()
    
    results = []
    for loan in loans:
        results.append({
            "loan_id": loan.id,
            "book": {
                "id": loan.book.id,
                "title": loan.book.title,
                "author": loan.book.author
            },
            "borrow_date": loan.borrow_date.isoformat(),
            "return_date": loan.return_date.isoformat() if loan.return_date else None,
            "status": loan.status
        })
        
    return jsonify({
        "user": {"id": user.id, "name": user.name},
        "loans": results
    })

# POST /users/{id}/loans - Thực hiện thao tác MƯỢN SÁCH cho người dùng
@app.route('/users/<int:user_id>/loans', methods=['POST'])
def borrow_book(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({"error": "book_id is required"}), 400
        
    book = Book.query.get_or_404(book_id)
    
    if book.available_copies <= 0:
        return jsonify({"error": "Book is currently out of stock"}), 400
        
    # Thực hiện mượn
    book.available_copies -= 1
    new_loan = Loan(user_id=user.id, book_id=book.id, status='borrowed')
    
    db.session.add(new_loan)
    db.session.commit()
    
    return jsonify({
        "message": "Book borrowed successfully",
        "loan_id": new_loan.id,
        "remaining_copies": book.available_copies
    }), 201

# ==========================================
# SETUP DỮ LIỆU MẪU BAN ĐẦU (SEEDING) 
# Chạy khi ứng dụng khởi động lần đầu
# ==========================================
def seed_data():
    if User.query.first():
        return # Database đã có dữ liệu
        
    print("Seeding initial data....")
    # Users
    u1 = User(name="Alice", email="alice@example.com")
    u2 = User(name="Bob", email="bob@example.com")
    db.session.add_all([u1, u2])
    
    # Books
    b1 = Book(title="Flask Web Development", author="Miguel Grinberg", published_year=2018, total_copies=3, available_copies=3)
    b2 = Book(title="Fluent Python", author="Luciano Ramalho", published_year=2015, total_copies=2, available_copies=2)
    b3 = Book(title="Clean Code", author="Robert C. Martin", published_year=2008, total_copies=5, available_copies=5)
    db.session.add_all([b1, b2, b3])
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tạo các bảng trong SQLite
        seed_data()      # Chèn dữ liệu mẫu
        
    app.run(debug=True, port=5000)
