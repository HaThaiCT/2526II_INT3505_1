import logging
import json
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging():
    """Setup logging with both file and console handlers"""
    # Create logger
    logger = logging.getLogger('library_api')
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # File handler - JSON format
    file_handler = logging.FileHandler('library_api.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Console handler - JSON format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Counter metrics
requests_total = Counter(
    'library_api_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

rate_limit_exceeded = Counter(
    'library_api_rate_limit_exceeded_total',
    'Total rate limit exceeded events',
    ['endpoint']
)

# Histogram metrics
request_duration = Histogram(
    'library_api_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'status'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

# Gauge metrics
active_requests = Gauge(
    'library_api_active_requests',
    'Number of active requests',
    ['endpoint']
)

books_in_system = Gauge(
    'library_api_books_count',
    'Total number of books in the system'
)


# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================

app = Flask(__name__)
logger = setup_logging()

# Rate limiter configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Temporary in-memory database for books
books_db = {
    "1": {"id": "1", "title": "Clean Code", "author": "Robert C. Martin", "available": 5},
    "2": {"id": "2", "title": "Design Patterns", "author": "Gang of Four", "available": 3},
    "3": {"id": "3", "title": "The Pragmatic Programmer", "author": "Hunt & Thomas", "available": 2},
}

books_in_system.set(len(books_db))


# ============================================================================
# MIDDLEWARE & DECORATORS
# ============================================================================

def track_metrics(f):
    """Decorator to track request metrics"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        endpoint = request.endpoint or "unknown"
        method = request.method
        
        # Increment active requests
        active_requests.labels(endpoint=endpoint).inc()
        
        # Track request duration
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            status = 200 if isinstance(result, dict) else result[1]
            return result
        except Exception as e:
            status = 500
            logger.error(f"Error in {endpoint}: {str(e)}")
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            request_duration.labels(method=method, endpoint=endpoint, status=status).observe(duration)
            active_requests.labels(endpoint=endpoint).dec()
            
            # Log request
            logger.info(f"Request completed", extra={
                'method': method,
                'endpoint': endpoint,
                'status': status,
                'duration': duration,
                'ip': request.remote_addr
            })
    
    return decorated_function


@app.before_request
def before_request():
    """Log incoming requests"""
    logger.debug(f"Incoming request: {request.method} {request.path}", extra={
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    })


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    endpoint = request.endpoint or "unknown"
    rate_limit_exceeded.labels(endpoint=endpoint).inc()
    
    logger.warning(f"Rate limit exceeded for endpoint: {endpoint}", extra={
        'endpoint': endpoint,
        'ip': request.remote_addr
    })
    
    return jsonify(error="Rate limit exceeded"), 429


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - no rate limiting"""
    logger.info("Health check requested")
    return jsonify(status="healthy", timestamp=datetime.utcnow().isoformat())


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    logger.debug("Metrics endpoint accessed")
    return Response(generate_latest(REGISTRY), mimetype='text/plain')


@app.route('/books', methods=['GET'])
@limiter.limit("30 per minute")
@track_metrics
def get_books():
    """Get all books - limited to 30 requests per minute"""
    logger.info("Fetching all books")
    return jsonify(books=list(books_db.values()))


@app.route('/books/<book_id>', methods=['GET'])
@limiter.limit("60 per minute")
@track_metrics
def get_book(book_id):
    """Get specific book - limited to 60 requests per minute"""
    logger.info(f"Fetching book with ID: {book_id}")
    
    if book_id not in books_db:
        logger.warning(f"Book not found: {book_id}")
        return jsonify(error="Book not found"), 404
    
    return jsonify(book=books_db[book_id])


@app.route('/books', methods=['POST'])
@limiter.limit("10 per minute")
@track_metrics
def create_book():
    """Create new book - limited to 10 requests per minute"""
    data = request.get_json()
    
    # Validation
    if not data or not all(k in data for k in ['title', 'author', 'available']):
        logger.warning("Invalid book creation request")
        return jsonify(error="Missing required fields"), 400
    
    book_id = str(len(books_db) + 1)
    new_book = {
        "id": book_id,
        "title": data['title'],
        "author": data['author'],
        "available": data['available']
    }
    
    books_db[book_id] = new_book
    books_in_system.set(len(books_db))
    
    logger.info(f"New book created: {book_id}", extra={
        'book_id': book_id,
        'title': data['title']
    })
    
    return jsonify(book=new_book), 201


@app.route('/books/<book_id>/borrow', methods=['POST'])
@limiter.limit("20 per minute")
@track_metrics
def borrow_book(book_id):
    """Borrow a book - limited to 20 requests per minute"""
    logger.info(f"Borrow request for book: {book_id}")
    
    if book_id not in books_db:
        logger.warning(f"Borrow failed - Book not found: {book_id}")
        return jsonify(error="Book not found"), 404
    
    book = books_db[book_id]
    if book['available'] <= 0:
        logger.warning(f"Borrow failed - No copies available: {book_id}")
        return jsonify(error="No copies available"), 400
    
    book['available'] -= 1
    logger.info(f"Book borrowed: {book_id}, remaining copies: {book['available']}")
    
    return jsonify(
        message="Book borrowed successfully",
        book=book
    )


@app.route('/books/<book_id>/return', methods=['POST'])
@limiter.limit("20 per minute")
@track_metrics
def return_book(book_id):
    """Return a book - limited to 20 requests per minute"""
    logger.info(f"Return request for book: {book_id}")
    
    if book_id not in books_db:
        logger.warning(f"Return failed - Book not found: {book_id}")
        return jsonify(error="Book not found"), 404
    
    book = books_db[book_id]
    book['available'] += 1
    
    logger.info(f"Book returned: {book_id}, available copies: {book['available']}")
    
    return jsonify(
        message="Book returned successfully",
        book=book
    )


@app.route('/books/<book_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@track_metrics
def delete_book(book_id):
    """Delete a book - limited to 5 requests per minute"""
    logger.info(f"Delete request for book: {book_id}")
    
    if book_id not in books_db:
        logger.warning(f"Delete failed - Book not found: {book_id}")
        return jsonify(error="Book not found"), 404
    
    del books_db[book_id]
    books_in_system.set(len(books_db))
    
    logger.info(f"Book deleted: {book_id}")
    
    return jsonify(message="Book deleted successfully")


@app.route('/stats', methods=['GET'])
@limiter.limit("30 per minute")
@track_metrics
def get_stats():
    """Get system statistics - limited to 30 requests per minute"""
    logger.info("Stats requested")
    
    stats = {
        'total_books': len(books_db),
        'total_available': sum(book['available'] for book in books_db.values()),
        'total_borrowed': sum(
            book.get('borrowed_count', 0) 
            for book in books_db.values()
        ),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(stats=stats)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"Not found: {request.path}")
    return jsonify(error="Endpoint not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify(error="Internal server error"), 500


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Library API Server")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False  # Set to False in production
    )
