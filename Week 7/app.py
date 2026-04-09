"""
Product Management API - Flask Backend với MongoDB
Demo về OpenAPI và Database Integration
"""

from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import os

app = Flask(__name__)

# ==================== CONFIGURATION ====================
# MongoDB Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/product_management")
mongo = PyMongo(app)

# Database collection
db = mongo.db.products


# ==================== HELPER FUNCTIONS ====================
def serialize_product(product):
    """Chuyển đổi MongoDB document sang JSON-serializable dict"""
    if product:
        product['_id'] = str(product['_id'])
        return product
    return None


def validate_product_input(data):
    """Validate dữ liệu đầu vào cho Product"""
    errors = []
    
    if 'name' not in data or not data['name'].strip():
        errors.append("Name is required")
    elif len(data['name']) > 200:
        errors.append("Name must not exceed 200 characters")
    
    if 'price' not in data:
        errors.append("Price is required")
    elif not isinstance(data['price'], (int, float)) or data['price'] < 0:
        errors.append("Price must be a positive number")
    
    if 'category' not in data or not data['category'].strip():
        errors.append("Category is required")
    elif len(data['category']) > 100:
        errors.append("Category must not exceed 100 characters")
    
    if 'description' in data and len(data.get('description', '')) > 1000:
        errors.append("Description must not exceed 1000 characters")
    
    if 'stock' in data:
        if not isinstance(data['stock'], int) or data['stock'] < 0:
            errors.append("Stock must be a non-negative integer")
    
    return errors


# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home route với API info"""
    return jsonify({
        "message": "Product Management API",
        "version": "1.0.0",
        "endpoints": {
            "GET /products": "Lấy tất cả sản phẩm",
            "POST /products": "Tạo sản phẩm mới",
            "GET /products/<id>": "Lấy một sản phẩm theo ID",
            "PUT /products/<id>": "Cập nhật sản phẩm",
            "DELETE /products/<id>": "Xóa sản phẩm"
        },
        "openapi_spec": "/openapi.yml"
    })


@app.route('/products', methods=['GET'])
def get_products():
    """
    GET /products
    Lấy danh sách tất cả sản phẩm
    """
    try:
        # Query parameters for filtering (optional)
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Build query
        query = {}
        if category:
            query['category'] = category
        if min_price is not None or max_price is not None:
            query['price'] = {}
            if min_price is not None:
                query['price']['$gte'] = min_price
            if max_price is not None:
                query['price']['$lte'] = max_price
        
        # Fetch products
        products = list(db.find(query))
        serialized_products = [serialize_product(p) for p in products]
        
        return jsonify({
            "success": True,
            "data": serialized_products,
            "count": len(serialized_products)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/products', methods=['POST'])
def create_product():
    """
    POST /products
    Tạo sản phẩm mới
    Request body: {name, description, price, category, stock}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        # Validate input
        errors = validate_product_input(data)
        if errors:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "details": errors
            }), 400
        
        # Prepare product document
        product = {
            "name": data['name'].strip(),
            "description": data.get('description', '').strip(),
            "price": float(data['price']),
            "category": data['category'].strip(),
            "stock": data.get('stock', 0),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = db.insert_one(product)
        product['_id'] = result.inserted_id
        
        return jsonify({
            "success": True,
            "data": serialize_product(product),
            "message": "Product created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/products/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """
    GET /products/<product_id>
    Lấy thông tin một sản phẩm theo ID
    """
    try:
        # Validate ObjectId
        try:
            obj_id = ObjectId(product_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "error": "Invalid product ID format"
            }), 400
        
        # Find product
        product = db.find_one({"_id": obj_id})
        
        if not product:
            return jsonify({
                "success": False,
                "error": "Product not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": serialize_product(product)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """
    PUT /products/<product_id>
    Cập nhật thông tin sản phẩm
    Request body: {name, description, price, category, stock}
    """
    try:
        # Validate ObjectId
        try:
            obj_id = ObjectId(product_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "error": "Invalid product ID format"
            }), 400
        
        # Check if product exists
        existing_product = db.find_one({"_id": obj_id})
        if not existing_product:
            return jsonify({
                "success": False,
                "error": "Product not found"
            }), 404
        
        # Get update data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        # Validate input
        errors = validate_product_input(data)
        if errors:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "details": errors
            }), 400
        
        # Prepare update document
        update_data = {
            "name": data['name'].strip(),
            "description": data.get('description', '').strip(),
            "price": float(data['price']),
            "category": data['category'].strip(),
            "stock": data.get('stock', 0),
            "updatedAt": datetime.utcnow()
        }
        
        # Update in MongoDB
        db.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        
        # Fetch updated product
        updated_product = db.find_one({"_id": obj_id})
        
        return jsonify({
            "success": True,
            "data": serialize_product(updated_product),
            "message": "Product updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    DELETE /products/<product_id>
    Xóa sản phẩm
    """
    try:
        # Validate ObjectId
        try:
            obj_id = ObjectId(product_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "error": "Invalid product ID format"
            }), 400
        
        # Check if product exists
        existing_product = db.find_one({"_id": obj_id})
        if not existing_product:
            return jsonify({
                "success": False,
                "error": "Product not found"
            }), 404
        
        # Delete from MongoDB
        db.delete_one({"_id": obj_id})
        
        return jsonify({
            "success": True,
            "message": "Product deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    print("🚀 Starting Product Management API...")
    print("📖 OpenAPI Spec: http://localhost:5000/openapi.yml")
    print("🔗 Database: MongoDB")
    print("=" * 50)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
