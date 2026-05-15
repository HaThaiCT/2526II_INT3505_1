# Webhook Integration - Quick Start Guide

Hướng dẫn nhanh 10 phút để bắt đầu với webhook system.

## ⚡ 10-Minute Setup

### Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### Step 2: Run the Server (30 sec)

```bash
python app.py
```

Output:
```
Starting Library API Server with Webhook Support
 * Running on http://0.0.0.0:5000
```

### Step 3: Register a Webhook (1 min)

In another terminal:

```bash
curl -X POST http://localhost:5000/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:5000/webhook-receiver",
    "events": ["book.created", "book.borrowed"],
    "active": true
  }'
```

Response:
```json
{
  "webhook_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Webhook registered successfully"
}
```

### Step 4: Create a Book (1 min)

This will trigger the webhook:

```bash
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Webhook Mastery",
    "author": "Expert Dev",
    "available": 5
  }'
```

Response:
```json
{
  "book": {
    "id": "4",
    "title": "Webhook Mastery",
    "author": "Expert Dev",
    "available": 5
  }
}
```

**What happened:**
- ✅ Book created
- ✅ `book.created` event triggered
- ✅ Webhook was called with signed payload
- ✅ Event stored in database

### Step 5: Check Events (1 min)

```bash
curl http://localhost:5000/events
```

Response:
```json
{
  "events": [
    {
      "id": "evt_550e8400...",
      "event_type": "book.created",
      "timestamp": "2024-01-15T10:30:45.123456",
      "data": {
        "id": "4",
        "title": "Webhook Mastery",
        "author": "Expert Dev",
        "available": 5
      }
    }
  ],
  "count": 1
}
```

### Step 6: List Webhooks (1 min)

```bash
curl http://localhost:5000/webhooks
```

Response:
```json
{
  "webhooks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "http://localhost:5000/webhook-receiver",
      "events": ["book.created", "book.borrowed"],
      "active": true,
      "created_at": "2024-01-15T10:30:45.123456",
      "successful_deliveries": 1,
      "failed_deliveries": 0,
      "retries": 3
    }
  ],
  "count": 1
}
```

### Step 7: View Prometheus Metrics (1 min)

```bash
curl http://localhost:5000/metrics | head -30
```

Output:
```
# HELP webhook_events_total Total webhook events triggered
# TYPE webhook_events_total counter
webhook_events_total{event_type="book.created",status="triggered"} 1.0

# HELP webhook_deliveries_total Total webhook delivery attempts
# TYPE webhook_deliveries_total counter
webhook_deliveries_total{destination="http",event_type="book.created",status="success"} 1.0
```

### Step 8: Run Full Test Suite (2 min)

In another terminal:

```bash
python test_webhooks.py
```

This runs 15 comprehensive tests.

---

## 📚 Common Tasks

### Register Multiple Event Types

```bash
curl -X POST http://localhost:5000/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhooks",
    "events": [
      "book.created",
      "book.borrowed",
      "book.returned",
      "book.deleted"
    ]
  }'
```

### Borrow and Return a Book (triggers webhooks)

```bash
# Borrow
curl -X POST http://localhost:5000/books/1/borrow

# Return
curl -X POST http://localhost:5000/books/1/return

# Check events
curl http://localhost:5000/events?type=book.borrowed
```

### Filter Events by Type

```bash
# Get only book.created events
curl http://localhost:5000/events?type=book.created

# Get only book.borrowed events
curl http://localhost:5000/events?type=book.borrowed&limit=5
```

### Get Webhook Details

```bash
curl http://localhost:5000/webhooks/{webhook_id}
```

### Delete Webhook

```bash
curl -X DELETE http://localhost:5000/webhooks/{webhook_id}
```

---

## 🔐 Security: Verify Signatures

### Python Client Example

```python
import hmac
import hashlib
import time
import json

WEBHOOK_SECRET = "your-secret-key-change-in-production"

def verify_webhook(request_body, signature_header):
    """Verify webhook signature"""
    try:
        parts = signature_header.split(',')
        version, timestamp, signature = parts
        
        # Check timestamp (prevent replay)
        if abs(int(time.time()) - int(timestamp)) > 300:
            print("❌ Signature too old")
            return False
        
        # Verify signature
        signed_content = f"{timestamp}.{request_body}"
        expected_sig = hmac.new(
            WEBHOOK_SECRET.encode(),
            signed_content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(signature, expected_sig):
            print("✅ Signature verified")
            return True
        else:
            print("❌ Signature invalid")
            return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# Usage (in Flask route):
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    signature = request.headers.get('X-Webhook-Signature')
    body = request.get_data(as_text=True)
    
    if not verify_webhook(body, signature):
        return 401
    
    data = request.get_json()
    # Process webhook
    return 200
```

---

## 🧪 Testing Webhooks

### Test with curl (manual)

```bash
# 1. Start app
python app.py

# 2. Create webhook
curl -X POST http://localhost:5000/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:5000/webhook-receiver",
    "events": ["book.created"]
  }'

# 3. Trigger event
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","author":"Me","available":1}'

# 4. Check events
curl http://localhost:5000/events
```

### Test with Python Script

```bash
python test_webhooks.py
```

This runs 15 tests including:
- ✅ Webhook registration
- ✅ Event triggering
- ✅ Signature verification
- ✅ Webhook delivery
- ✅ Rate limiting
- ✅ Metrics collection

---

## 📊 Webhook Lifecycle Example

### Scenario: User Creates a Book

```
1. API Request
   POST /books
   {
     "title": "Python 101",
     "author": "John Doe",
     "available": 3
   }

2. Book Created
   ✓ Stored in database
   ✓ Book ID = "4"

3. Event Generated
   event_type: "book.created"
   event_id: "evt_550e8400..."
   timestamp: "2024-01-15T10:30:45Z"
   data: { complete book object }

4. Webhooks Triggered
   Found 2 matching webhooks
   
5. Signature Generated
   HMAC-SHA256(secret, timestamp.payload)
   
6. HTTP POST Sent
   Headers: X-Webhook-Signature, X-Webhook-ID, ...
   
7. Response Received
   Status: 200 OK
   
8. Metrics Updated
   webhook_events_total++
   webhook_deliveries_total++
   webhook_delivery_latency_seconds updated

9. Event Logged
   Event stored in events list
   Available via /events endpoint
```

---

## 🚨 Troubleshooting

### Server Won't Start

```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process (Windows)
taskkill /PID <PID> /F

# Try different port
python app.py  # Uses 5000 by default
```

### Webhook Not Being Called

```bash
# 1. Check webhook is registered
curl http://localhost:5000/webhooks

# 2. Check events are being generated
curl http://localhost:5000/events

# 3. Check webhook URL is accessible
curl http://localhost:5000/webhook-receiver

# 4. Check logs in console
```

### Signature Verification Failed

```bash
# Make sure:
1. WEBHOOK_SECRET matches on both sides
2. Timestamp is within 5 minutes
3. Request body hasn't been modified
4. Using correct header name (X-Webhook-Signature)
```

### Rate Limiting Issues

```bash
# Check current rate limits
GET /books  # 30/min
GET /webhooks  # 50/min
POST /books  # 10/min

# Wait 1 minute for limit to reset
```

---

## 📈 Monitoring & Debugging

### View Metrics

```bash
# Raw Prometheus format
curl http://localhost:5000/metrics

# Specific metric
curl http://localhost:5000/metrics | grep webhook_events_total

# In Prometheus UI
http://localhost:9090
Query: webhook_events_total
```

### Check Event Details

```bash
# List all events
curl http://localhost:5000/events

# Filter by type
curl http://localhost:5000/events?type=book.created

# Get specific event
curl http://localhost:5000/events/{event_id}

# Limit results
curl http://localhost:5000/events?limit=5
```

### Monitor Webhook Deliveries

```bash
# Via metrics
curl http://localhost:5000/metrics | grep webhook_deliveries

# Via events
curl http://localhost:5000/events

# Via webhook details
curl http://localhost:5000/webhooks/{webhook_id}
```

---

## 🎯 Next Steps

1. ✅ Understand webhook basics (this guide)
2. ✅ Run test suite (`python test_webhooks.py`)
3. ✅ Read [API_PATTERNS_ANALYSIS.md](API_PATTERNS_ANALYSIS.md)
4. ✅ Study [WEBHOOK_PATTERNS.md](WEBHOOK_PATTERNS.md)
5. ⚪ Integrate with external services
6. ⚪ Setup monitoring (Prometheus + Grafana)
7. ⚪ Implement exponential backoff retry

---

## 💡 Tips & Tricks

### Quickly Test Webhook

Use RequestBin-like service:
```bash
# Visit https://requestbin.com/
# Copy your unique URL
# Register webhook with that URL
# Watch requests arrive in real-time
```

### Debug Signature Issues

```python
# Log what you're signing
timestamp = "1614618000"
payload = '{"data": "value"}'
signed_content = f"{timestamp}.{payload}"
print(f"Signing: {signed_content}")

# Calculate signature
sig = hmac.new(SECRET.encode(), signed_content.encode(), hashlib.sha256).hexdigest()
print(f"Signature: {sig}")
```

### Test Rate Limiting

```bash
# Make 35 requests (limit is 30/min for /books)
for i in {1..35}; do
  curl http://localhost:5000/books
  echo "Request $i"
  sleep 0.1
done

# Should see 429 (Too Many Requests) on attempts 31-35
```

---

## 📞 Common Commands

```bash
# Health check
curl http://localhost:5000/health

# List all webhooks
curl http://localhost:5000/webhooks

# List all books
curl http://localhost:5000/books

# List all events
curl http://localhost:5000/events

# View metrics
curl http://localhost:5000/metrics

# Run tests
python test_webhooks.py

# Create a webhook
curl -X POST http://localhost:5000/webhooks \
  -H "Content-Type: application/json" \
  -d '{"url":"http://example.com/webhook","events":["book.created"]}'
```

---

## 📚 Documentation Files

- **README.md** - Full overview
- **API_PATTERNS_ANALYSIS.md** - Stripe vs GitHub patterns
- **WEBHOOK_PATTERNS.md** - Implementation patterns
- **QUICKSTART.md** - This file

---

## ✅ Checklist

- [ ] Installed dependencies
- [ ] Server running on port 5000
- [ ] Registered webhook
- [ ] Created book (triggered event)
- [ ] Checked events
- [ ] Verified webhook delivery
- [ ] Ran test suite
- [ ] Read API patterns analysis
- [ ] Understood signature verification

---

**Next:** Run `python test_webhooks.py` to test everything!
