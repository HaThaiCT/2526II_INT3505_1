# Library API System - Webhook Integration & Notifications

Một dự án API Library System hoàn chỉnh với tích hợp webhook, hệ thống thông báo, và patterns từ Stripe & GitHub API.

## 🎯 Features

- ✅ **Webhook System** - Event-driven notifications
- ✅ **Security** - HMAC-SHA256 signature verification
- ✅ **Multiple Event Types** - book.created, book.borrowed, etc.
- ✅ **Notification Channels** - HTTP, Email, Slack (simulated)
- ✅ **Event Management** - Track all events
- ✅ **Metrics & Monitoring** - Prometheus integration
- ✅ **Rate Limiting** - Per-endpoint limits
- ✅ **Retry Logic** - Automatic retry on failure

## 📁 Project Structure

```
Week 11/
├── app.py                              # Main Flask app with webhooks
├── requirements.txt                    # Python dependencies
├── test_webhooks.py                    # Comprehensive test suite
├── webhook_client.py                   # Webhook client for testing
│
├── README.md                           # This file
├── API_PATTERNS_ANALYSIS.md            # Stripe vs GitHub analysis
├── WEBHOOK_PATTERNS.md                 # Detailed webhook patterns
├── QUICKSTART.md                       # Quick start guide
│
└── webhook_events.log                  # Generated at runtime
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

Server starts at `http://localhost:5000`

### 3. Test Webhooks

In another terminal:

```bash
python test_webhooks.py
```

### 4. View API

```bash
# Health check
curl http://localhost:5000/health

# List webhooks
curl http://localhost:5000/webhooks

# Get events
curl http://localhost:5000/events
```

---

## 📨 Webhook Events

### Supported Events

| Event Type | Trigger | Data |
|------------|---------|------|
| `book.created` | When new book is added | Book details |
| `book.borrowed` | When book is borrowed | Book info + borrow count |
| `book.returned` | When book is returned | Book info + return count |
| `book.deleted` | When book is deleted | Deleted book details |

### Event Payload Format

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "book.created",
  "timestamp": "2024-01-15T10:30:45.123456",
  "data": {
    "id": "1",
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "available": 5
  }
}
```

### Headers Sent with Webhook

```
X-Webhook-ID: 550e8400-e29b-41d4-a716-446655440000
X-Webhook-Signature: v1,1614618000,5257a869...
X-Webhook-Timestamp: 1614618000
Content-Type: application/json
```

---

## 🔐 Security

### Signature Verification

All webhooks are signed using HMAC-SHA256. To verify:

```python
import hmac
import hashlib
import time

WEBHOOK_SECRET = "your-secret-key"

# Extract signature header
signature_header = request.headers.get('X-Webhook-Signature')
# Format: v1,<timestamp>,<signature>

# Verify
def verify_signature(body, signature):
    parts = signature.split(',')
    version, timestamp, sig = parts
    
    # Check timestamp (prevent replay)
    if abs(int(time.time()) - int(timestamp)) > 300:
        return False
    
    # Compute expected signature
    signed_content = f"{timestamp}.{body}"
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        signed_content.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison
    return hmac.compare_digest(sig, expected_sig)
```

---

## 🔌 API Endpoints

### Webhook Management

#### Register Webhook

```bash
POST /webhooks

Request:
{
  "url": "https://example.com/webhook",
  "events": ["book.created", "book.borrowed"],
  "active": true
}

Response:
{
  "webhook_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Webhook registered successfully"
}
```

#### List Webhooks

```bash
GET /webhooks

Response:
{
  "webhooks": [
    {
      "id": "550e8400...",
      "url": "https://example.com/webhook",
      "events": ["book.created", "book.borrowed"],
      "active": true,
      "created_at": "2024-01-15T10:30:45.123456",
      "successful_deliveries": 5,
      "failed_deliveries": 0
    }
  ],
  "count": 1
}
```

#### Get Webhook Details

```bash
GET /webhooks/{webhook_id}

Response:
{
  "webhook": { /* webhook object */ }
}
```

#### Delete Webhook

```bash
DELETE /webhooks/{webhook_id}

Response:
{
  "message": "Webhook deleted successfully"
}
```

### Event Management

#### List Events

```bash
GET /events?type=book.created&limit=50

Response:
{
  "events": [ /* event objects */ ],
  "count": 10
}
```

#### Get Event Details

```bash
GET /events/{event_id}

Response:
{
  "event": { /* event object */ }
}
```

### Book Operations (with webhook triggers)

#### Create Book

```bash
POST /books

Request:
{
  "title": "Python Programming",
  "author": "Mark Lutz",
  "available": 3
}

Response (201):
{
  "book": { /* book object */ }
}

Side Effect: Triggers `book.created` webhook to all subscribers
```

#### Borrow Book

```bash
POST /books/{book_id}/borrow

Response:
{
  "message": "Book borrowed",
  "book": { /* updated book */ }
}

Side Effect: Triggers `book.borrowed` webhook
```

#### Return Book

```bash
POST /books/{book_id}/return

Response:
{
  "message": "Book returned",
  "book": { /* updated book */ }
}

Side Effect: Triggers `book.returned` webhook
```

#### Delete Book

```bash
DELETE /books/{book_id}

Response:
{
  "message": "Book deleted"
}

Side Effect: Triggers `book.deleted` webhook
```

---

## 🧪 Testing

### Run Full Test Suite

```bash
python test_webhooks.py
```

### Manual Testing with Webhook Client

```bash
# Start receiver (simulates external service)
# Already running on http://localhost:5000/webhook-receiver

# Register webhook
curl -X POST http://localhost:5000/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:5000/webhook-receiver",
    "events": ["book.created", "book.borrowed"],
    "active": true
  }'

# Create book (triggers webhook)
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Book",
    "author": "Author Name",
    "available": 2
  }'

# Check events
curl http://localhost:5000/events
```

---

## 📊 Monitoring

### Prometheus Metrics

**Access:** `http://localhost:5000/metrics`

**Available Metrics:**

```
# Webhook events
webhook_events_total{event_type="book.created",status="triggered"}

# Webhook deliveries
webhook_deliveries_total{event_type="book.created",destination="http",status="success"}

# Delivery latency
webhook_delivery_latency_seconds{event_type="book.created",destination="http"}

# Active webhooks count
active_webhooks_count

# Notification queue size
notification_queue_size
```

### Sample Queries

```promql
# Webhook delivery rate
rate(webhook_deliveries_total[1m])

# Success rate
sum(rate(webhook_deliveries_total{status="success"}[1m])) 
/ 
sum(rate(webhook_deliveries_total[1m]))

# Average delivery latency
avg(webhook_delivery_latency_seconds)

# 95th percentile latency
histogram_quantile(0.95, webhook_delivery_latency_seconds_bucket)
```

---

## 🏗️ Architecture

### Event Flow

```
User Action (Create Book)
    ↓
API Endpoint (POST /books)
    ↓
Create Event object
    ↓
Trigger Event (webhook_manager.trigger_event)
    ↓
Find matching webhooks
    ↓
Send notifications to each webhook
    ├→ HTTP Webhook (with signature)
    ├→ Email Notification
    └→ Slack Notification (simulated)
    ↓
Record metrics (Prometheus)
    ↓
Log events
```

### Component Architecture

```
┌─────────────────────────────────┐
│      Flask Application          │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────────┐   │
│  │    Book Management      │   │
│  │  (CRUD operations)      │   │
│  └────────────┬────────────┘   │
│               │                 │
│               ↓                 │
│  ┌─────────────────────────┐   │
│  │   Event System          │   │
│  │  - Event creation       │   │
│  │  - Event tracking       │   │
│  └────────────┬────────────┘   │
│               │                 │
│               ↓                 │
│  ┌─────────────────────────┐   │
│  │  Webhook Manager        │   │
│  │  - Register webhooks    │   │
│  │  - Manage subscriptions │   │
│  └────────────┬────────────┘   │
│               │                 │
│               ↓                 │
│  ┌─────────────────────────┐   │
│  │  Notification Service   │   │
│  │  - HTTP delivery        │   │
│  │  - Email notification   │   │
│  │  - Slack notification   │   │
│  │  - Retry logic          │   │
│  └────────────┬────────────┘   │
│               │                 │
└───────────────┼─────────────────┘
                │
    ┌───────────┼───────────┐
    ↓           ↓           ↓
External    Email      Slack
Webhook   Service    Service
Server
```

---

## 🔄 Retry Logic

### Default Retry Configuration

```
Attempt 1: Immediately
Attempt 2: After 30 seconds
Attempt 3: After 2 minutes
Attempt 4: After 10 minutes

Total: ~12.5 minutes max retry window
```

### Retry Decision Logic

```python
if response.status_code in [200, 201, 202]:
    # Success - don't retry
    return True
elif response.status_code >= 500:
    # Server error - retry
    return False
elif response.status_code == 429:
    # Rate limited - retry with backoff
    return False
elif response.status_code in [400, 401, 403]:
    # Client error - don't retry (config error)
    return False
else:
    # Other - retry
    return False
```

---

## 📋 API Patterns Applied

### From Stripe ✅

1. **HMAC-SHA256 Signatures**
   - Prevents tampering
   - Replay attack prevention
   - Industry standard

2. **Event-based Architecture**
   - Decoupled systems
   - Scalable
   - Real-time updates

3. **Clear Event Types**
   - `resource.action` format
   - Easy filtering
   - Self-documenting

### From GitHub ✅

1. **Comprehensive Headers**
   - Event identification
   - Timestamp validation
   - Webhook tracking

2. **Idempotent Operations**
   - Safe to retry
   - Deduplication
   - No side effects

3. **Detailed Event Context**
   - Full resource state
   - Change tracking
   - Rich debugging info

---

## 🛠️ Configuration

### Environment Variables

```bash
# Webhook secret (used for HMAC signing)
export WEBHOOK_SECRET="your-secret-key-here"

# Flask configuration
export FLASK_ENV="production"
export FLASK_DEBUG="False"
```

### Rate Limiting

| Endpoint | Limit |
|----------|-------|
| `/webhooks` GET | 50/min |
| `/webhooks` POST | 10/min |
| `/webhooks/<id>` GET | 50/min |
| `/webhooks/<id>` DELETE | 10/min |
| `/events` GET | 30/min |
| `/events/<id>` GET | 50/min |
| `/books` GET | 30/min |
| `/books` POST | 10/min |
| `/books/<id>` POST (borrow/return) | 20/min |
| `/books/<id>` DELETE | 5/min |

---

## ❌ Error Handling

### Common Errors

#### 400 Bad Request
```json
{
  "error": "Missing url or events"
}
```

#### 401 Unauthorized (Webhook verification)
```json
{
  "error": "Invalid signature"
}
```

#### 404 Not Found
```json
{
  "error": "Webhook not found"
}
```

#### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## 📚 Documentation Files

- **README.md** (this file) - Overview and quick reference
- **API_PATTERNS_ANALYSIS.md** - Detailed comparison with Stripe & GitHub
- **WEBHOOK_PATTERNS.md** - Implementation patterns and best practices
- **QUICKSTART.md** - Step-by-step getting started guide

---

## 🎓 Learning Resources

### Implementation Patterns

1. **Event-Driven Architecture**
   - Decouples producers and consumers
   - Enables real-time updates
   - Scales easily

2. **Webhook Delivery**
   - HTTP callbacks
   - Signature verification
   - Retry strategies

3. **Security Best Practices**
   - HMAC signing
   - Timestamp validation
   - Constant-time comparison

---

## 🚀 Future Enhancements

1. **Exponential Backoff**
   - More sophisticated retry policy
   - Better resource utilization

2. **Event Batching**
   - Send multiple events per request
   - Reduced overhead

3. **Webhook Testing**
   - Test event delivery
   - Delivery debugging

4. **Advanced Filtering**
   - Filter by resource ID
   - Filter by status changes

5. **Dead Letter Queue**
   - Persistent storage of failed events
   - Event replay capability

6. **OAuth Integration**
   - Secure authentication
   - User-specific webhooks

---

## 📞 Support

For issues or questions:
1. Check [API_PATTERNS_ANALYSIS.md](API_PATTERNS_ANALYSIS.md)
2. Review [WEBHOOK_PATTERNS.md](WEBHOOK_PATTERNS.md)
3. Run test suite: `python test_webhooks.py`

---

## 📝 Development Notes

- Event ID is UUID for global uniqueness
- Timestamps are ISO 8601 format
- Signatures use HMAC-SHA256
- All timestamps in UTC
- Rate limits per endpoint
- Metrics exported to Prometheus

---

## ✅ Implementation Checklist

- [x] Flask application setup
- [x] Webhook registration/management
- [x] Event system
- [x] Notification service
- [x] HMAC-SHA256 signing
- [x] Signature verification
- [x] Retry logic
- [x] HTTP delivery
- [x] Prometheus metrics
- [x] Test suite
- [x] API patterns analysis
- [x] Documentation

---

**Created:** May 14, 2026  
**Framework:** Flask (Python)  
**Patterns:** Stripe + GitHub  
**Security:** HMAC-SHA256  
**Monitoring:** Prometheus
