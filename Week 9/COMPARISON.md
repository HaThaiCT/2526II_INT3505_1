# 📊 SO SÁNH CHI TIẾT: v1 vs v2

Tài liệu này so sánh chi tiết giữa v1 (deprecated) và v2 (current) của Payment API.

---

## 🔄 Request Structure Comparison

### Creating a Payment

#### v1 Request (Flat Structure)
```http
POST /api/v1/payments HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "amount": 100.00,
  "currency": "USD",
  "customer_id": "CUST123",
  "customer_email": "john@example.com",
  "method": "card"
}
```

#### v2 Request (Nested Structure)
```http
POST /api/v2/payments HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Idempotency-Key: unique-key-abc123

{
  "amount": {
    "value": 100.00,
    "currency": "USD"
  },
  "customer": {
    "id": "CUST123",
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "+1234567890"
  },
  "payment_method": {
    "type": "card",
    "details": {
      "card_type": "visa",
      "last4": "4242"
    },
    "provider": "stripe"
  },
  "metadata": {
    "order_id": "ORD-456",
    "source": "web",
    "campaign": "summer_sale"
  }
}
```

**Key Differences:**
- ✅ v2 groups related fields (amount, customer, payment_method)
- ✅ v2 có thêm optional fields (name, phone, details, provider)
- ✅ v2 hỗ trợ Idempotency-Key header
- ✅ v2 có flexible metadata object

---

## 📤 Response Structure Comparison

### v1 Response
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "amount": 100.00,
    "currency": "USD",
    "customer_id": "CUST123",
    "customer_email": "john@example.com",
    "method": "card",
    "status": "pending",
    "createdAt": "2026-04-23T10:00:00Z",
    "updatedAt": "2026-04-23T10:00:00Z"
  },
  "message": "Payment created successfully",
  "deprecation_warning": "This endpoint is deprecated. Please use /api/v2/payments. This version will be removed on 2026-12-31."
}
```

**Response Headers:**
```http
HTTP/1.1 201 Created
Content-Type: application/json
Deprecation: true
Sunset: 2026-12-31
Link: </api/v2/docs>; rel="alternate"
X-API-Warn: This API version is deprecated and will be removed on 2026-12-31. Please migrate to v2.
```

### v2 Response
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "amount": {
      "value": 100.00,
      "currency": "USD"
    },
    "customer": {
      "id": "CUST123",
      "email": "john@example.com",
      "name": "John Doe",
      "phone": "+1234567890"
    },
    "payment_method": {
      "type": "card",
      "details": {
        "card_type": "visa",
        "last4": "4242"
      },
      "provider": "stripe"
    },
    "metadata": {
      "order_id": "ORD-456",
      "source": "web"
    },
    "status": "pending",
    "createdAt": "2026-04-23T10:00:00Z",
    "updatedAt": "2026-04-23T10:00:00Z"
  },
  "message": "Payment created successfully",
  "version": "2.0.0"
}
```

**Response Headers:**
```http
HTTP/1.1 201 Created
Content-Type: application/json
```

**Key Differences:**
- ⚠️ v1 có deprecation warning trong body và headers
- ✅ v2 không có deprecation warnings
- ✅ v2 có nested structure consistent với request
- ✅ v2 có version field

---

## 🎯 Feature Comparison Matrix

| Feature | v1 | v2 | Notes |
|---------|----|----|-------|
| **Basic CRUD** | ✅ | ✅ | Both support create, read, list |
| **Nested Structure** | ❌ | ✅ | v2 groups related fields |
| **Supported Currencies** | USD, EUR, VND | USD, EUR, VND, **JPY, GBP** | v2 adds 2 more |
| **Customer Details** | Limited | Full | v2 has name, phone |
| **Payment Method Details** | Simple string | Rich object | v2 has provider, details |
| **Metadata Support** | ❌ | ✅ | v2 allows custom metadata |
| **Idempotency** | ❌ | ✅ | v2 supports via headers |
| **Refund Operation** | ❌ | ✅ | v2 only |
| **Payment History** | ❌ | ✅ | v2 only |
| **Query Filters** | Limited | Enhanced | v2 has more options |
| **Deprecation Headers** | ⚠️ Yes | ❌ No | v1 warns users |
| **Update Support** | Limited | Flexible | v2 allows partial updates |

---

## 🔧 All Operations Comparison

### 1. List Payments

#### v1: Basic Listing
```bash
GET /api/v1/payments

# No filtering supported
```

#### v2: Advanced Filtering
```bash
GET /api/v2/payments?status=pending&currency=USD&customer_id=CUST123

# Supports:
# - status: pending, completed, failed, refunded
# - currency: USD, EUR, VND, JPY, GBP
# - customer_id: any string
```

---

### 2. Get Single Payment

#### v1
```bash
GET /api/v1/payments/507f1f77bcf86cd799439011

Response: Flat structure
```

#### v2
```bash
GET /api/v2/payments/507f1f77bcf86cd799439011

Response: Nested structure with full details
```

---

### 3. Update Payment

#### v1: Not implemented
```bash
PUT /api/v1/payments/507f1f77bcf86cd799439011

❌ Not available in v1
```

#### v2: Flexible Updates
```bash
PUT /api/v2/payments/507f1f77bcf86cd799439011
Content-Type: application/json

{
  "status": "completed",
  "metadata": {
    "completed_by": "admin"
  }
}

✅ Partial updates supported
```

---

### 4. Refund Payment (NEW in v2)

#### v1
```bash
❌ Not available
```

#### v2
```bash
POST /api/v2/payments/507f1f77bcf86cd799439011/refund
Content-Type: application/json

{
  "amount": 50.00,
  "reason": "Customer request"
}

✅ Full or partial refunds
```

---

### 5. Payment History (NEW in v2)

#### v1
```bash
❌ Not available
```

#### v2
```bash
GET /api/v2/payments/507f1f77bcf86cd799439011/history

Response:
{
  "success": true,
  "payment_id": "507f1f77bcf86cd799439011",
  "history": [
    {
      "event": "created",
      "timestamp": "2026-04-23T10:00:00Z",
      "status": "pending"
    },
    {
      "event": "completed",
      "timestamp": "2026-04-23T10:05:00Z",
      "status": "completed"
    },
    {
      "event": "refunded",
      "timestamp": "2026-04-23T11:00:00Z",
      "status": "refunded",
      "details": {
        "amount": 50.00,
        "reason": "Customer request"
      }
    }
  ]
}
```

---

## 💾 Database Schema Evolution

### Internal Storage (Always v2 format)

```javascript
// MongoDB document structure (v2)
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "amount": {
    "value": 100.00,
    "currency": "USD"
  },
  "customer": {
    "id": "CUST123",
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "+1234567890"
  },
  "payment_method": {
    "type": "card",
    "details": {
      "card_type": "visa",
      "last4": "4242"
    },
    "provider": "stripe"
  },
  "metadata": {
    "migrated_from_v1": false,
    "order_id": "ORD-456"
  },
  "status": "pending",
  "createdAt": ISODate("2026-04-23T10:00:00Z"),
  "updatedAt": ISODate("2026-04-23T10:00:00Z")
}
```

**When v1 creates payment:**
1. Accepts flat structure
2. Converts to v2 internally
3. Stores as v2
4. Converts back to v1 for response
5. Adds `metadata.migrated_from_v1: true` flag

**When v2 creates payment:**
1. Accepts nested structure
2. Stores directly as v2
3. Returns v2 format
4. No conversion needed

---

## 🔀 Conversion Logic

### v1 → v2 Conversion
```python
def convert_v1_to_v2(v1_data):
    """Convert v1 flat structure to v2 nested structure"""
    return {
        "amount": {
            "value": v1_data["amount"],
            "currency": v1_data["currency"]
        },
        "customer": {
            "id": v1_data["customer_id"],
            "email": v1_data.get("customer_email", ""),
            "name": "",  # Not available in v1
            "phone": ""  # Not available in v1
        },
        "payment_method": {
            "type": v1_data["method"],
            "details": {},
            "provider": ""
        },
        "metadata": {
            "migrated_from_v1": True,
            "original_timestamp": str(v1_data.get("createdAt", ""))
        },
        "status": v1_data.get("status", "pending"),
        "createdAt": v1_data.get("createdAt", datetime.utcnow()),
        "updatedAt": datetime.utcnow()
    }
```

### v2 → v1 Conversion
```python
def convert_v2_to_v1(v2_data):
    """Convert v2 nested structure to v1 flat structure"""
    return {
        "_id": v2_data.get("_id"),
        "amount": v2_data["amount"]["value"],
        "currency": v2_data["amount"]["currency"],
        "customer_id": v2_data["customer"]["id"],
        "customer_email": v2_data["customer"].get("email"),
        "method": v2_data["payment_method"]["type"],
        "status": v2_data.get("status"),
        "createdAt": v2_data.get("createdAt"),
        "updatedAt": v2_data.get("updatedAt")
    }
```

---

## 📈 Migration Path Examples

### Example 1: Simple Card Payment

**v1 Code (Old):**
```python
import requests

response = requests.post('http://api.example.com/api/v1/payments', json={
    'amount': 100.00,
    'currency': 'USD',
    'customer_id': 'CUST123',
    'method': 'card'
})
```

**v2 Code (New):**
```python
import requests

response = requests.post('http://api.example.com/api/v2/payments', 
    json={
        'amount': {
            'value': 100.00,
            'currency': 'USD'
        },
        'customer': {
            'id': 'CUST123'
        },
        'payment_method': {
            'type': 'card'
        }
    },
    headers={
        'Idempotency-Key': f'order-{order_id}'  # NEW: Prevent duplicates
    }
)
```

---

### Example 2: Bank Transfer with Details

**v1 Code:**
```python
# Limited information
response = requests.post('http://api.example.com/api/v1/payments', json={
    'amount': 500.00,
    'currency': 'EUR',
    'customer_id': 'CUST456',
    'customer_email': 'jane@example.com',
    'method': 'bank'  # Just a string
})
```

**v2 Code:**
```python
# Rich details
response = requests.post('http://api.example.com/api/v2/payments', json={
    'amount': {
        'value': 500.00,
        'currency': 'EUR'
    },
    'customer': {
        'id': 'CUST456',
        'email': 'jane@example.com',
        'name': 'Jane Smith',  # NEW
        'phone': '+49123456789'  # NEW
    },
    'payment_method': {
        'type': 'bank_transfer',  # More specific
        'details': {  # NEW
            'iban': 'DE89370400440532013000',
            'bic': 'COBADEFFXXX'
        },
        'provider': 'wise'  # NEW
    },
    'metadata': {  # NEW: Custom data
        'order_id': 'ORD-789',
        'source': 'mobile_app',
        'campaign': 'spring_promo'
    }
})
```

---

## 🎯 Why These Changes?

### 1. Nested Structure
**Problem in v1:** Flat structure becomes crowded
```json
{
  "customer_id": "...",
  "customer_email": "...",
  "customer_name": "...",
  "customer_phone": "...",
  "customer_address_line1": "...",
  "customer_address_city": "..."
}
```

**Solution in v2:** Group related fields
```json
{
  "customer": {
    "id": "...",
    "email": "...",
    "name": "...",
    "phone": "...",
    "address": {
      "line1": "...",
      "city": "..."
    }
  }
}
```

### 2. Extensibility
**v1:** Hard to add new fields without breaking
```json
{
  "method": "card"  // How to add card details?
}
```

**v2:** Easy to extend
```json
{
  "payment_method": {
    "type": "card",
    "details": {  // Can add any card info here
      "card_type": "visa",
      "last4": "4242",
      "exp_month": 12,
      "exp_year": 2028
    }
  }
}
```

### 3. Better Semantics
**v1:** `method` is ambiguous
**v2:** `payment_method.type` is clear

### 4. Future-Proof
v2 structure allows adding:
- Multiple payment methods per transaction
- Recurring payments
- Split payments
- Complex refund rules
- Webhook configurations

---

## 🏆 Best Practices Demonstrated

### ✅ Do's

1. **Give Long Notice**
   - 6+ months deprecation period
   - Multiple reminders
   - Clear sunset date

2. **Provide Migration Tools**
   - Detailed migration guide
   - Code examples
   - Conversion helpers

3. **Maintain Backward Compatibility**
   - v1 still works during transition
   - Internal conversion layer
   - No data migration needed

4. **Clear Communication**
   - Deprecation headers
   - Warning messages
   - Version numbers

5. **Add Value in New Version**
   - New features (refund, history)
   - Better structure
   - Enhanced capabilities

### ❌ Don'ts

1. **Don't Break Without Warning**
   - Always announce deprecation
   - Give reasonable timeline

2. **Don't Remove Documentation**
   - Keep v1 docs until sunset
   - Provide side-by-side comparison

3. **Don't Force Immediate Migration**
   - Allow dual-version support
   - Gradual transition period

---

## 📊 Summary Table

| Aspect | v1 | v2 | Winner |
|--------|----|----|--------|
| **Structure** | Flat | Nested | v2 |
| **Extensibility** | Limited | High | v2 |
| **Features** | Basic | Enhanced | v2 |
| **Currencies** | 3 | 5 | v2 |
| **Metadata** | No | Yes | v2 |
| **Idempotency** | No | Yes | v2 |
| **Refunds** | No | Yes | v2 |
| **History** | No | Yes | v2 |
| **Simplicity** | Higher | Lower | v1 |
| **Learning Curve** | Easy | Moderate | v1 |
| **Status** | Deprecated | Current | v2 |

---

**Conclusion:** v2 is clearly superior for long-term maintainability and feature growth, even though it has slightly more complexity upfront. The nested structure and enhanced features make it worth the migration effort.

---

**Document Version:** 1.0.0  
**Last Updated:** April 23, 2026  
**Related:** [README.md](README.md) | [UPGRADE_STRATEGY.md](UPGRADE_STRATEGY.md)
