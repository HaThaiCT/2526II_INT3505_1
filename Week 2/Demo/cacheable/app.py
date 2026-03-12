"""
REST API Principle: Cacheable
Mô tả: Response có thể được cache để cải thiện hiệu suất,
       sử dụng HTTP cache headers
"""

from flask import Flask, jsonify, make_response, request
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import time

app = Flask(__name__)

# Dữ liệu mẫu - sản phẩm (ít thay đổi, nên cache)
products = [
    {"id": 1, "name": "Laptop Dell XPS", "price": 1500, "category": "Electronics"},
    {"id": 2, "name": "iPhone 15", "price": 999, "category": "Electronics"},
    {"id": 3, "name": "Python Book", "price": 35, "category": "Books"},
    {"id": 4, "name": "Wireless Mouse", "price": 25, "category": "Accessories"}
]

# Dữ liệu thay đổi theo thời gian (không nên cache)
user_activities = []

# Decorator để thêm cache headers
def cache_control(max_age=300, public=True):
    """
    Thêm Cache-Control header vào response
    max_age: thời gian cache tính bằng giây
    public: True = cache được share, False = cache riêng từng user
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            
            # Thêm Cache-Control
            cache_type = 'public' if public else 'private'
            response.headers['Cache-Control'] = f'{cache_type}, max-age={max_age}'
            
            # Thêm Expires header
            expires = datetime.utcnow() + timedelta(seconds=max_age)
            response.headers['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # Thêm timestamp để dễ test
            response.headers['X-Generated-At'] = datetime.utcnow().isoformat()
            
            return response
        return decorated_function
    return decorator

# Root endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Cacheable API Demo",
        "description": "Sử dụng HTTP cache headers để tối ưu hiệu suất",
        "endpoints": {
            "GET /api/products": "Danh sách sản phẩm (cache 5 phút)",
            "GET /api/products/:id": "Chi tiết sản phẩm (cache 2 phút)",
            "GET /api/products/no-cache": "Sản phẩm không cache",
            "GET /api/products/etag": "Sản phẩm với ETag",
            "GET /api/activities": "Hoạt động user (không cache)",
            "POST /api/activities": "Thêm hoạt động"
        }
    }), 200

# GET - Danh sách sản phẩm (cache 5 phút)
@app.route('/api/products', methods=['GET'])
@cache_control(max_age=300, public=True)  # Cache 5 phút
def get_products():
    """
    Response được cache trong 5 phút
    Client/Browser/Proxy có thể sử dụng cached data
    """
    time.sleep(0.5)  # Giả lập query database chậm
    
    return jsonify({
        "success": True,
        "cached_for": "5 minutes",
        "count": len(products),
        "data": products,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# GET - Chi tiết sản phẩm (cache 2 phút)
@app.route('/api/products/<int:product_id>', methods=['GET'])
@cache_control(max_age=120, public=True)  # Cache 2 phút
def get_product(product_id):
    """
    Response được cache trong 2 phút
    """
    time.sleep(0.3)  # Giả lập query chậm
    
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return jsonify({
            "success": True,
            "cached_for": "2 minutes",
            "data": product,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    return jsonify({
        "success": False,
        "error": "Product not found"
    }), 404

# GET - Sản phẩm không cache
@app.route('/api/products/no-cache', methods=['GET'])
def get_products_no_cache():
    """
    Dữ liệu không được cache
    Luôn lấy data mới nhất từ server
    """
    response = make_response(jsonify({
        "success": True,
        "cached": False,
        "data": products,
        "timestamp": datetime.utcnow().isoformat()
    }))
    
    # Không cho phép cache
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response, 200

# GET - Sản phẩm với ETag (conditional request)
@app.route('/api/products/etag', methods=['GET'])
def get_products_etag():
    """
    Sử dụng ETag để kiểm tra xem dữ liệu có thay đổi không
    Nếu không đổi, trả về 304 Not Modified (tiết kiệm băng thông)
    """
    # Tạo ETag từ hash của dữ liệu
    data_str = str(products)
    etag = hashlib.md5(data_str.encode()).hexdigest()
    
    # Kiểm tra If-None-Match header từ client
    if_none_match = request.headers.get('If-None-Match')
    
    if if_none_match == etag:
        # Dữ liệu không thay đổi, trả về 304
        response = make_response('', 304)
        response.headers['ETag'] = etag
        return response
    
    # Dữ liệu thay đổi, trả về full response
    response = make_response(jsonify({
        "success": True,
        "data": products,
        "timestamp": datetime.utcnow().isoformat()
    }))
    
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=60'
    
    return response, 200

# GET - Hoạt động user (private, không cache)
@app.route('/api/activities', methods=['GET'])
def get_activities():
    """
    Dữ liệu cá nhân không nên cache public
    Sử dụng private cache nếu cần
    """
    response = make_response(jsonify({
        "success": True,
        "cached": False,
        "data": user_activities,
        "timestamp": datetime.utcnow().isoformat()
    }))
    
    # Private data - không cache hoặc cache riêng
    response.headers['Cache-Control'] = 'private, no-cache, must-revalidate'
    
    return response, 200

# POST - Thêm hoạt động
@app.route('/api/activities', methods=['POST'])
def add_activity():
    """
    Thêm hoạt động mới
    """
    data = request.get_json()
    
    activity = {
        "id": len(user_activities) + 1,
        "action": data.get('action', 'unknown'),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    user_activities.append(activity)
    
    return jsonify({
        "success": True,
        "data": activity
    }), 201

# GET - Cache stats
@app.route('/api/cache-info', methods=['GET'])
def cache_info():
    """
    Thông tin về cache configuration
    """
    return jsonify({
        "success": True,
        "cache_configuration": {
            "/api/products": {
                "max_age": 300,
                "type": "public",
                "description": "Cache 5 phút"
            },
            "/api/products/:id": {
                "max_age": 120,
                "type": "public",
                "description": "Cache 2 phút"
            },
            "/api/products/no-cache": {
                "max_age": 0,
                "type": "no-cache",
                "description": "Không cache"
            },
            "/api/products/etag": {
                "max_age": 60,
                "type": "public with ETag",
                "description": "Cache 1 phút + ETag validation"
            },
            "/api/activities": {
                "max_age": 0,
                "type": "private, no-cache",
                "description": "Dữ liệu cá nhân, không cache"
            }
        }
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("CACHEABLE API DEMO")
    print("=" * 60)
    print("Server running on: http://localhost:5003")
    print("\nCache Configuration:")
    print("  /api/products         - Cache 5 phút (public)")
    print("  /api/products/:id     - Cache 2 phút (public)")
    print("  /api/products/no-cache - Không cache")
    print("  /api/products/etag    - ETag validation")
    print("  /api/activities       - Private, no cache")
    print("\nTip: Gọi cùng một endpoint nhiều lần để thấy cache hoạt động")
    print("     Kiểm tra headers: Cache-Control, Expires, ETag")
    print("=" * 60)
    app.run(debug=True, port=5003)
