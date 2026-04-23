"""
Payment API - API Versioning Demo (v1 -> v2)
Demo về chiến lược versioning và deprecation cho REST API
"""

from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)

# ==================== CONFIGURATION ====================
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/payment_api")
mongo = PyMongo(app)
db = mongo.db.payments

# Deprecation configuration
V1_SUNSET_DATE = "2026-12-31"  # v1 sẽ bị tắt vào cuối năm 2026
V1_DEPRECATION_DATE = "2026-06-01"  # v1 đã được đánh dấu deprecated


# ==================== DECORATORS ====================
def add_deprecation_headers(sunset_date=V1_SUNSET_DATE):
    """Decorator để thêm deprecation headers cho v1 endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers['Deprecation'] = 'true'
            response.headers['Sunset'] = sunset_date
            response.headers['Link'] = '</api/v2/docs>; rel="alternate"'
            response.headers['X-API-Warn'] = f'This API version is deprecated and will be removed on {sunset_date}. Please migrate to v2.'
            return response
        return decorated_function
    return decorator


# ==================== HELPER FUNCTIONS ====================
def serialize_payment(payment):
    """Chuyển đổi MongoDB document sang JSON"""
    if payment:
        payment['_id'] = str(payment['_id'])
        return payment
    return None


def validate_payment_v1(data):
    """Validate dữ liệu v1 payment"""
    errors = []
    
    if 'amount' not in data or not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
        errors.append("Amount must be a positive number")
    
    if 'currency' not in data or data['currency'] not in ['USD', 'EUR', 'VND']:
        errors.append("Currency must be USD, EUR, or VND")
    
    if 'customer_id' not in data or not data['customer_id'].strip():
        errors.append("Customer ID is required")
    
    if 'method' not in data or data['method'] not in ['card', 'bank', 'wallet']:
        errors.append("Method must be card, bank, or wallet")
    
    return errors


def validate_payment_v2(data):
    """Validate dữ liệu v2 payment (có thêm fields mới)"""
    errors = []
    
    if 'amount' not in data:
        errors.append("Amount is required")
    else:
        if not isinstance(data['amount'], dict):
            errors.append("Amount must be an object with value and currency")
        else:
            if 'value' not in data['amount'] or not isinstance(data['amount']['value'], (int, float)) or data['amount']['value'] <= 0:
                errors.append("Amount value must be a positive number")
            if 'currency' not in data['amount'] or data['amount']['currency'] not in ['USD', 'EUR', 'VND', 'JPY', 'GBP']:
                errors.append("Currency must be USD, EUR, VND, JPY, or GBP")
    
    if 'customer' not in data or not isinstance(data['customer'], dict):
        errors.append("Customer must be an object")
    else:
        if 'id' not in data['customer'] or not data['customer']['id'].strip():
            errors.append("Customer ID is required")
        if 'email' in data['customer']:
            email = data['customer']['email']
            if '@' not in email:
                errors.append("Invalid email format")
    
    if 'payment_method' not in data or not isinstance(data['payment_method'], dict):
        errors.append("Payment method must be an object")
    else:
        if 'type' not in data['payment_method'] or data['payment_method']['type'] not in ['card', 'bank_transfer', 'digital_wallet', 'crypto']:
            errors.append("Payment method type must be card, bank_transfer, digital_wallet, or crypto")
    
    if 'metadata' in data and not isinstance(data['metadata'], dict):
        errors.append("Metadata must be an object")
    
    return errors


def convert_v1_to_v2(v1_data):
    """Chuyển đổi v1 payment sang v2 format"""
    return {
        "amount": {
            "value": v1_data.get('amount'),
            "currency": v1_data.get('currency')
        },
        "customer": {
            "id": v1_data.get('customer_id'),
            "email": v1_data.get('customer_email', '')
        },
        "payment_method": {
            "type": v1_data.get('method'),
            "details": {}
        },
        "metadata": {
            "migrated_from_v1": True,
            "original_timestamp": v1_data.get('createdAt', datetime.utcnow()).isoformat() if isinstance(v1_data.get('createdAt'), datetime) else str(v1_data.get('createdAt', ''))
        },
        "status": v1_data.get('status', 'pending'),
        "createdAt": v1_data.get('createdAt', datetime.utcnow()),
        "updatedAt": datetime.utcnow()
    }


def convert_v2_to_v1(v2_data):
    """Chuyển đổi v2 payment sang v1 format để hiển thị"""
    return {
        "_id": v2_data.get('_id'),
        "amount": v2_data.get('amount', {}).get('value'),
        "currency": v2_data.get('amount', {}).get('currency'),
        "customer_id": v2_data.get('customer', {}).get('id'),
        "customer_email": v2_data.get('customer', {}).get('email'),
        "method": v2_data.get('payment_method', {}).get('type'),
        "status": v2_data.get('status'),
        "createdAt": v2_data.get('createdAt'),
        "updatedAt": v2_data.get('updatedAt')
    }


# ==================== ROOT ROUTES ====================
@app.route('/')
def home():
    """API Info"""
    return jsonify({
        "name": "Payment API",
        "description": "API Demo về versioning và deprecation strategy",
        "versions": {
            "v1": {
                "status": "deprecated",
                "sunset_date": V1_SUNSET_DATE,
                "base_url": "/api/v1",
                "docs": "/api/v1/docs"
            },
            "v2": {
                "status": "current",
                "base_url": "/api/v2",
                "docs": "/api/v2/docs"
            }
        },
        "deprecation_notice": f"v1 is deprecated and will be removed on {V1_SUNSET_DATE}. Please migrate to v2.",
        "migration_guide": "/migration-guide"
    })


@app.route('/migration-guide')
def migration_guide():
    """Migration guide từ v1 sang v2"""
    return jsonify({
        "title": "Migration Guide: v1 to v2",
        "overview": "This guide helps you migrate from v1 to v2 of the Payment API",
        "timeline": {
            "deprecation_announced": V1_DEPRECATION_DATE,
            "sunset_date": V1_SUNSET_DATE,
            "grace_period": "6 months"
        },
        "breaking_changes": [
            {
                "change": "Amount structure changed",
                "v1": "Flat fields: amount, currency",
                "v2": "Nested object: amount: {value, currency}",
                "migration": "Wrap amount and currency in an amount object"
            },
            {
                "change": "Customer information restructured",
                "v1": "Flat fields: customer_id, customer_email",
                "v2": "Nested object: customer: {id, email, name, phone}",
                "migration": "Wrap customer fields in a customer object"
            },
            {
                "change": "Payment method enhanced",
                "v1": "Simple string: method",
                "v2": "Nested object: payment_method: {type, details, provider}",
                "migration": "Wrap method in payment_method object with type field"
            },
            {
                "change": "Additional currencies supported",
                "v1": "USD, EUR, VND",
                "v2": "USD, EUR, VND, JPY, GBP",
                "migration": "No changes needed for existing currencies"
            }
        ],
        "new_features": [
            "Enhanced payment method details",
            "Customer metadata support",
            "Additional currency support",
            "Better error messages",
            "Idempotency keys support",
            "Webhook support"
        ],
        "migration_steps": [
            "1. Review the breaking changes and new schema",
            "2. Update your request body structure to match v2",
            "3. Test with v2 endpoints in development",
            "4. Update error handling for new error formats",
            "5. Deploy to production before sunset date"
        ],
        "support": "For questions: api-support@example.com"
    })


# ==================== API V1 ROUTES (DEPRECATED) ====================
@app.route('/api/v1/docs')
@add_deprecation_headers()
def v1_docs():
    """v1 API Documentation"""
    return jsonify({
        "version": "1.0.0",
        "status": "DEPRECATED",
        "deprecation_notice": {
            "message": f"This API version is deprecated and will be removed on {V1_SUNSET_DATE}",
            "sunset_date": V1_SUNSET_DATE,
            "alternative": "/api/v2/docs",
            "migration_guide": "/migration-guide"
        },
        "endpoints": {
            "GET /api/v1/payments": "List all payments",
            "POST /api/v1/payments": "Create a payment",
            "GET /api/v1/payments/{id}": "Get payment by ID",
            "PUT /api/v1/payments/{id}": "Update payment"
        }
    })


@app.route('/api/v1/payments', methods=['GET'])
@add_deprecation_headers()
def v1_get_payments():
    """v1: Lấy danh sách payments"""
    try:
        payments = list(db.find({}))
        # Convert v2 format to v1 format for backward compatibility
        v1_payments = [convert_v2_to_v1(serialize_payment(p)) for p in payments]
        
        return jsonify({
            "success": True,
            "data": v1_payments,
            "count": len(v1_payments),
            "deprecation_warning": f"This endpoint is deprecated. Please use /api/v2/payments. This version will be removed on {V1_SUNSET_DATE}."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/v1/payments', methods=['POST'])
@add_deprecation_headers()
def v1_create_payment():
    """v1: Tạo payment mới (internally converts to v2)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body required"}), 400
        
        # Validate v1 format
        errors = validate_payment_v1(data)
        if errors:
            return jsonify({"success": False, "error": "Validation failed", "details": errors}), 400
        
        # Convert v1 to v2 internally
        v2_payment = convert_v1_to_v2(data)
        result = db.insert_one(v2_payment)
        v2_payment['_id'] = result.inserted_id
        
        # Convert back to v1 format for response
        v1_response = convert_v2_to_v1(v2_payment)
        
        return jsonify({
            "success": True,
            "data": serialize_payment(v1_response),
            "message": "Payment created successfully",
            "deprecation_warning": f"This endpoint is deprecated. Please use /api/v2/payments. This version will be removed on {V1_SUNSET_DATE}."
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/v1/payments/<payment_id>', methods=['GET'])
@add_deprecation_headers()
def v1_get_payment(payment_id):
    """v1: Lấy payment theo ID"""
    try:
        try:
            obj_id = ObjectId(payment_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid payment ID"}), 400
        
        payment = db.find_one({"_id": obj_id})
        if not payment:
            return jsonify({"success": False, "error": "Payment not found"}), 404
        
        v1_payment = convert_v2_to_v1(serialize_payment(payment))
        
        return jsonify({
            "success": True,
            "data": v1_payment,
            "deprecation_warning": f"This endpoint is deprecated. Please use /api/v2/payments/{payment_id}. This version will be removed on {V1_SUNSET_DATE}."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== API V2 ROUTES (CURRENT) ====================
@app.route('/api/v2/docs')
def v2_docs():
    """v2 API Documentation"""
    return jsonify({
        "version": "2.0.0",
        "status": "CURRENT",
        "base_url": "/api/v2",
        "endpoints": {
            "GET /api/v2/payments": "List all payments with enhanced data",
            "POST /api/v2/payments": "Create a payment with new structure",
            "GET /api/v2/payments/{id}": "Get payment by ID",
            "PUT /api/v2/payments/{id}": "Update payment",
            "POST /api/v2/payments/{id}/refund": "Refund a payment (NEW)",
            "GET /api/v2/payments/{id}/history": "Get payment history (NEW)"
        },
        "whats_new": [
            "Enhanced payment structure with nested objects",
            "Additional currency support (JPY, GBP)",
            "Customer metadata and enhanced details",
            "Payment method details and provider info",
            "Refund support",
            "Payment history tracking",
            "Better error messages",
            "Idempotency support"
        ]
    })


@app.route('/api/v2/payments', methods=['GET'])
def v2_get_payments():
    """v2: Lấy danh sách payments"""
    try:
        # Query parameters
        status = request.args.get('status')
        currency = request.args.get('currency')
        customer_id = request.args.get('customer_id')
        
        query = {}
        if status:
            query['status'] = status
        if currency:
            query['amount.currency'] = currency
        if customer_id:
            query['customer.id'] = customer_id
        
        payments = list(db.find(query))
        serialized = [serialize_payment(p) for p in payments]
        
        return jsonify({
            "success": True,
            "data": serialized,
            "count": len(serialized),
            "version": "2.0.0"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "version": "2.0.0"}), 500


@app.route('/api/v2/payments', methods=['POST'])
def v2_create_payment():
    """v2: Tạo payment mới"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body required"}), 400
        
        # Validate v2 format
        errors = validate_payment_v2(data)
        if errors:
            return jsonify({"success": False, "error": "Validation failed", "details": errors}), 400
        
        # Prepare payment document
        payment = {
            "amount": {
                "value": float(data['amount']['value']),
                "currency": data['amount']['currency']
            },
            "customer": {
                "id": data['customer']['id'],
                "email": data['customer'].get('email', ''),
                "name": data['customer'].get('name', ''),
                "phone": data['customer'].get('phone', '')
            },
            "payment_method": {
                "type": data['payment_method']['type'],
                "details": data['payment_method'].get('details', {}),
                "provider": data['payment_method'].get('provider', '')
            },
            "metadata": data.get('metadata', {}),
            "status": "pending",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Handle idempotency
        idempotency_key = request.headers.get('Idempotency-Key')
        if idempotency_key:
            existing = db.find_one({"metadata.idempotency_key": idempotency_key})
            if existing:
                return jsonify({
                    "success": True,
                    "data": serialize_payment(existing),
                    "message": "Payment already exists (idempotent)",
                    "version": "2.0.0"
                }), 200
            payment['metadata']['idempotency_key'] = idempotency_key
        
        result = db.insert_one(payment)
        payment['_id'] = result.inserted_id
        
        return jsonify({
            "success": True,
            "data": serialize_payment(payment),
            "message": "Payment created successfully",
            "version": "2.0.0"
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "version": "2.0.0"}), 500


@app.route('/api/v2/payments/<payment_id>', methods=['GET'])
def v2_get_payment(payment_id):
    """v2: Lấy payment theo ID"""
    try:
        try:
            obj_id = ObjectId(payment_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid payment ID format"}), 400
        
        payment = db.find_one({"_id": obj_id})
        if not payment:
            return jsonify({"success": False, "error": "Payment not found"}), 404
        
        return jsonify({
            "success": True,
            "data": serialize_payment(payment),
            "version": "2.0.0"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "version": "2.0.0"}), 500


@app.route('/api/v2/payments/<payment_id>', methods=['PUT'])
def v2_update_payment(payment_id):
    """v2: Cập nhật payment"""
    try:
        try:
            obj_id = ObjectId(payment_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid payment ID format"}), 400
        
        existing = db.find_one({"_id": obj_id})
        if not existing:
            return jsonify({"success": False, "error": "Payment not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Request body required"}), 400
        
        # Partial update allowed in v2
        update_fields = {}
        if 'status' in data:
            update_fields['status'] = data['status']
        if 'metadata' in data:
            update_fields['metadata'] = {**existing.get('metadata', {}), **data['metadata']}
        
        update_fields['updatedAt'] = datetime.utcnow()
        
        db.update_one({"_id": obj_id}, {"$set": update_fields})
        updated = db.find_one({"_id": obj_id})
        
        return jsonify({
            "success": True,
            "data": serialize_payment(updated),
            "message": "Payment updated successfully",
            "version": "2.0.0"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "version": "2.0.0"}), 500


@app.route('/api/v2/payments/<payment_id>/refund', methods=['POST'])
def v2_refund_payment(payment_id):
    """v2: Hoàn tiền payment (NEW in v2)"""
    try:
        try:
            obj_id = ObjectId(payment_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid payment ID format"}), 400
        
        payment = db.find_one({"_id": obj_id})
        if not payment:
            return jsonify({"success": False, "error": "Payment not found"}), 404
        
        if payment.get('status') == 'refunded':
            return jsonify({"success": False, "error": "Payment already refunded"}), 400
        
        data = request.get_json() or {}
        refund_amount = data.get('amount', payment['amount']['value'])
        
        # Update payment status
        db.update_one(
            {"_id": obj_id},
            {
                "$set": {
                    "status": "refunded",
                    "refund": {
                        "amount": refund_amount,
                        "reason": data.get('reason', ''),
                        "refundedAt": datetime.utcnow()
                    },
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        refunded = db.find_one({"_id": obj_id})
        
        return jsonify({
            "success": True,
            "data": serialize_payment(refunded),
            "message": "Payment refunded successfully",
            "version": "2.0.0"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "version": "2.0.0"}), 500


@app.route('/api/v2/payments/<payment_id>/history', methods=['GET'])
def v2_payment_history(payment_id):
    """v2: Lấy lịch sử payment (NEW in v2)"""
    try:
        try:
            obj_id = ObjectId(payment_id)
        except InvalidId:
            return jsonify({"success": False, "error": "Invalid payment ID format"}), 400
        
        payment = db.find_one({"_id": obj_id})
        if not payment:
            return jsonify({"success": False, "error": "Payment not found"}), 404
        
        # Build history from payment data
        history = [
            {
                "event": "created",
                "timestamp": payment.get('createdAt'),
                "status": "pending"
            }
        ]
        
        if payment.get('status') == 'completed':
            history.append({
                "event": "completed",
                "timestamp": payment.get('updatedAt'),
                "status": "completed"
            })
        
        if payment.get('status') == 'refunded':
            history.append({
                "event": "refunded",
                "timestamp": payment.get('refund', {}).get('refundedAt'),
                "status": "refunded",
                "details": payment.get('refund', {})
            })
        
        return jsonify({
            "success": True,
            "payment_id": str(payment['_id']),
            "history": history,
            "version": "2.0.0"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "version": "2.0.0"}), 500


# ==================== RUN ====================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
