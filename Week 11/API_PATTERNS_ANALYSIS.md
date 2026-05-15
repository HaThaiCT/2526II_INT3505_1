# API Patterns Analysis: Stripe vs GitHub vs Our Implementation

Phân tích các patterns từ Stripe & GitHub API và áp dụng vào Library API System.

## 📊 Executive Summary

| Pattern | Stripe | GitHub | Our Implementation |
|---------|--------|--------|-------------------|
| Webhook Signature | HMAC-SHA256 | HMAC-SHA256 | ✅ HMAC-SHA256 |
| Timestamp Validation | Yes (5 min) | Yes (5 min) | ✅ Yes (5 min) |
| Webhook Headers | X-Stripe-* | X-Hub-* | ✅ X-Webhook-* |
| Retry Policy | Exponential backoff | 25 attempts/25 hours | ✅ Configurable |
| Event Format | event_type + data | action + object | ✅ event_type + data |
| Idempotency | Idempotency-Key | N/A | ✅ event.id |
| Rate Limiting | API-specific | Per token | ✅ Per endpoint |

---

## 🔐 Security Patterns

### 1. **Signature Verification (HMAC-SHA256)**

#### Stripe Pattern
```
Signature header: X-Stripe-Signature: t=1614618000,v1=5257a869e7ecebeda32affa2d530bd0c6e4d5b5a86b0f1234567890123456789

Format: t=<timestamp>,v1=<signature>

Verification:
1. signed_content = timestamp.payload
2. compute_signature = HMAC_SHA256(secret, signed_content)
3. compare with provided signature
```

#### GitHub Pattern
```
Signature header: X-Hub-Signature-256: sha256=52b582138706...

Format: algorithm=hex_encoded_hash

Verification:
1. compute_hash = HMAC_SHA256(secret, request_body)
2. compare with provided hash
```

#### Our Implementation ✅
```python
# Combines both patterns for added security
signature_format = "v1,<timestamp>,<hash>"

# Verification includes:
1. Timestamp validation (prevent replay attacks)
2. HMAC-SHA256 verification
3. Timing-safe comparison (hmac.compare_digest)

# Additional security:
- Separate timestamp in signature (prevents timing attacks)
- 5-minute window (replay attack prevention)
```

### 2. **Authentication Methods**

| Method | Stripe | GitHub | Our API |
|--------|--------|--------|---------|
| API Keys | ✅ Bearer token | ✅ Token | ⚪ Optional |
| OAuth 2.0 | ✅ Yes | ✅ Yes | ⚪ Future |
| Webhook Secret | ✅ Yes | ✅ Yes | ✅ Yes |
| IP Whitelist | ✅ Yes | ⚪ No | ⚪ Future |

---

## 📨 Webhook Patterns

### 1. **Event Format**

#### Stripe Format
```json
{
  "id": "evt_1Nwf...",
  "object": "event",
  "api_version": "2023-10-16",
  "created": 1614618000,
  "type": "charge.succeeded",
  "data": {
    "object": { /* charge object */ },
    "previous_attributes": {}
  }
}
```

#### GitHub Format
```json
{
  "action": "opened",
  "issue": { /* issue object */ },
  "pull_request": { /* PR object */ },
  "repository": { /* repo object */ },
  "sender": { /* user object */ }
}
```

#### Our Format ✅
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

**Pattern Decisions:**
- `event_id`: Idempotency key (like Stripe's event.id)
- `event_type`: Clear event namespace (like GitHub's action)
- `timestamp`: ISO 8601 format (standard)
- `data`: Actual resource (clean payload)

### 2. **Event Types & Naming Convention**

#### Stripe Convention
```
charge.succeeded
charge.failed
dispute.created
customer.created
```
Pattern: `<resource>.<action>`

#### GitHub Convention
```
issues.opened
issues.closed
pull_request.opened
push (for repository)
```
Pattern: `<resource>.<action>` or `<action>`

#### Our Convention ✅
```
book.created        (create operation)
book.updated        (update operation)
book.deleted        (delete operation)
book.borrowed       (custom action)
book.returned       (custom action)
```

**Advantages:**
- Clear semantic meaning
- Easy to filter subscriptions
- Consistent with REST resource model
- Extensible for custom events

---

## 🔄 Retry & Delivery Patterns

### 1. **Stripe Retry Policy**

```
Attempt 1: Immediately
Attempt 2: 5 minutes
Attempt 3: 30 minutes
Attempt 4: 2 hours
Attempt 5: 5 hours
Attempt 6: 10 hours
Attempt 7: 24 hours
Attempt 8: 24 hours

Total: 5 days retry window
```

### 2. **GitHub Retry Policy**

```
Attempt 1: Immediately
Retry attempts: Up to 25 times over 25 hours
Exponential backoff: 10 seconds to 60 minutes

Headers:
X-GitHub-Delivery: Request ID
X-GitHub-Hook-ID: Hook ID
X-GitHub-Hook-Installation-Target-ID: Installation ID
```

### 3. **Our Retry Policy** ✅

```python
# Configurable per webhook
retries: 3
backoff_strategy: exponential
timeout: 5 seconds

# Implementation:
attempt 1: immediate
attempt 2: after 30 seconds
attempt 3: after 2 minutes
attempt 4: after 10 minutes

# Dead letter queue for failed events
failed_events: maintained for analysis
```

---

## 📡 HTTP Headers Patterns

### Stripe Headers
```http
X-Stripe-Signature: t=1614618000,v1=5257a869...
Stripe-Version: 2023-10-16
User-Agent: Stripe/1.0 (+https://stripe.com)
```

### GitHub Headers
```http
X-Hub-Signature-256: sha256=52b582138706...
X-Hub-Delivery: 12345-67890-...
X-GitHub-Event: push
X-GitHub-Hook-ID: 123456789
X-GitHub-Hook-Installation-Target-ID: 987654321
User-Agent: GitHub-Hookshot/xxxxxxx
```

### Our Headers ✅
```http
X-Webhook-ID: 550e8400-e29b-41d4-a716-446655440000
X-Webhook-Signature: v1,1614618000,5257a869...
X-Webhook-Timestamp: 1614618000
Content-Type: application/json
```

**Design Rationale:**
- Standard X- prefix for custom headers
- Clear namespace (Webhook)
- Timestamp separate (prevent timing attacks)
- Consistent with industry standards

---

## 🎯 Webhook Subscription Patterns

### Stripe Endpoint Configuration
```
Supported events to send:
- charge.succeeded
- charge.failed
- customer.created
- etc.

Can select:
- Specific events
- All events (*)
- Custom event types
```

### GitHub Webhook Configuration
```
Events:
- push
- pull_request
- issues
- release
- etc.

Can select:
- Individual events
- All events
```

### Our Implementation ✅
```python
# Register with event filter
POST /webhooks
{
  "url": "https://example.com/webhook",
  "events": ["book.created", "book.borrowed", "book.deleted"],
  "active": true
}

# Supports:
- Array of events
- Wildcard (future)
- Event filters (future)
```

---

## 🔌 Webhook Delivery Methods

### 1. **Synchronous Delivery** (Our current)
```
Request → Process Immediately → Return 200 OK
↓
Retry on failure (3 times)
```

### 2. **Asynchronous Delivery** (Enterprise pattern)
```
Request → Queue Event → Return 202 Accepted
↓ (Background job)
Process & Deliver → Retry on failure
```

### 3. **Event Sourcing Pattern**
```
Request → Store Event → Return 200 OK
↓
Publish Event to Bus → Queue delivery
↓
Multiple subscribers receive event
```

**Our Evolution Path:**
```
Week 11: Synchronous (current)
Week 12: Add queue (asyncio/Celery)
Week 13: Event sourcing
```

---

## 💾 Data Consistency Patterns

### Idempotency Pattern

#### Stripe
```
Uses event.id as idempotency key
Even if same event is delivered multiple times,
system recognizes it's the same event
```

#### GitHub
```
Uses delivery ID + timestamp
Allows client to deduplicate
```

#### Our Implementation ✅
```python
class Event:
    id = uuid4()  # Unique event ID
    event_type = "book.created"
    timestamp = datetime.utcnow()
    data = {...}

# Usage: Client can use event.id to deduplicate
# Event ID stays same even if re-delivered
```

---

## 🔍 Monitoring & Analytics Patterns

### Stripe Webhook Metrics
```
- Event attempts (successful/failed)
- Delivery latency
- Error rates by endpoint
- Event volumes by type
```

### GitHub Webhook Metrics
```
- Recent deliveries
- Delivery success rate
- Response time
- Error breakdown
```

### Our Implementation ✅
```python
# Prometheus metrics
webhook_events: Total events triggered
webhook_deliveries: Delivery attempts by destination/status
webhook_latency: Delivery time distribution
active_webhooks: Current webhook count
notification_queue_size: Pending notifications
```

---

## 🏗️ API Response Patterns

### Standard Response Format

#### Stripe API
```json
{
  "object": "charge",
  "id": "ch_1...",
  "amount": 2000,
  "created": 1614618000,
  "status": "succeeded"
}
```

#### GitHub API
```json
{
  "id": 1,
  "node_id": "MDQ6VXNlcjE=",
  "login": "octocat",
  "created_at": "2011-01-26T19:01:12Z"
}
```

#### Our API ✅
```json
{
  "webhook": {
    "id": "550e8400...",
    "url": "https://example.com/webhook",
    "events": ["book.created"],
    "active": true,
    "created_at": "2024-01-15T10:30:45.123456Z"
  }
}
```

---

## ⚠️ Error Handling Patterns

### Stripe Error Response
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Too many requests",
    "type": "invalid_request_error"
  }
}
```

### GitHub Error Response
```json
{
  "message": "Validation Failed",
  "errors": [
    {
      "message": "The listed users and repositories cannot be mixed...",
      "resource": "Search",
      "field": "q"
    }
  ]
}
```

### Our Error Response ✅
```json
{
  "error": "Webhook not found",
  "error_code": "webhook_not_found",
  "timestamp": "2024-01-15T10:30:45.123456Z"
}
```

---

## 📋 API Versioning Patterns

### Stripe
```
Header: Stripe-Version: 2023-10-16
- Date-based versioning
- Backward compatibility maintained
- Clients can pin version
```

### GitHub
```
Header: Accept: application/vnd.github.v3+json
- Version in Accept header
- Explicit version selection
```

### Our Approach (Future) ✅
```
URL-based: /v1/webhooks
Header-based: Accept: application/vnd.library.v1+json
- Flexible versioning
- Multiple versions supported simultaneously
```

---

## 🎓 Key Learnings Applied

### ✅ What We Adopted from Stripe

1. **HMAC-SHA256 Signature Verification**
   - Industry standard
   - Proven secure
   - Timestamp-based replay protection

2. **Event-based Architecture**
   - Decoupled systems
   - Scalable
   - Easy to add subscribers

3. **Clear Event Types**
   - `resource.action` naming
   - Self-documenting
   - Easy filtering

### ✅ What We Adopted from GitHub

1. **Comprehensive Headers**
   - Event ID for tracking
   - Timestamp for validation
   - Hook ID for identification

2. **Idempotent Operations**
   - Safe to retry
   - Event IDs for deduplication
   - No side effects on duplicate

3. **Detailed Events**
   - Include action context
   - Resource state changes
   - Previous state tracking

### ✅ What We Improved

1. **Security**
   - Timestamp validation with tolerance
   - Constant-time comparison
   - Separate timestamp in signature

2. **Simplicity**
   - Cleaner payload structure
   - Clear event types
   - Easier to parse

3. **Flexibility**
   - Configurable retry policy
   - Multiple notification channels
   - Easy to extend

---

## 🚀 Implementation Best Practices

### 1. **Always Verify Signatures**
```python
# Bad ❌
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    data = request.get_json()
    # Process without verification

# Good ✅
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    if not verify_webhook_signature(request.get_data(), headers['X-Webhook-Signature']):
        return 401
    data = request.get_json()
```

### 2. **Idempotent Processing**
```python
# Bad ❌
def process_webhook(event):
    update_database(event.data)
    send_email(event.data)

# Good ✅
def process_webhook(event):
    if event_id_already_processed(event.id):
        return  # Already handled
    
    update_database(event.data)
    send_email(event.data)
    mark_event_processed(event.id)
```

### 3. **Implement Retry Logic**
```python
# Bad ❌
def send_webhook(url, payload):
    requests.post(url, json=payload)

# Good ✅
def send_webhook(url, payload, retries=3):
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code in [200, 201, 202]:
                return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    return False
```

### 4. **Monitor Delivery**
```python
# Bad ❌
# No tracking of webhook deliveries

# Good ✅
webhook_delivery_metrics = {
    'total_attempts': 0,
    'successful': 0,
    'failed': 0,
    'average_latency': 0
}
```

---

## 📚 Comparison Table: Detailed Features

| Feature | Stripe | GitHub | Our Library API |
|---------|--------|--------|-----------------|
| **Signature** | HMAC-SHA256 | HMAC-SHA256 | ✅ HMAC-SHA256 |
| **Event ID** | Unique UUID | Delivery ID | ✅ UUID |
| **Timestamp** | Unix timestamp | ISO 8601 | ✅ ISO 8601 |
| **Retry** | 5 days | 25 hours | ✅ Configurable |
| **Event Types** | 100+ | 30+ | ✅ 5+ (extensible) |
| **Filtering** | By event type | By event type | ✅ By event type |
| **Testing** | Event browser | Delivery info | ✅ Built-in receiver |
| **Rate Limiting** | API-specific | Per token | ✅ Per endpoint |
| **Monitoring** | Full dashboard | Simple view | ✅ Prometheus metrics |

---

## 🎯 Future Enhancements (Week 12+)

1. **Exponential Backoff Retry**
   - Current: Fixed intervals
   - Future: Exponential backoff (like Stripe)

2. **Event Batching**
   - Current: Individual events
   - Future: Batch delivery

3. **Webhook Testing**
   - Current: Manual testing
   - Future: Stripe-style test events

4. **Webhook Filtering**
   - Current: Event type only
   - Future: Advanced filtering (resource ID, status)

5. **Dead Letter Queue**
   - Current: Failed events logged
   - Future: Persistent storage with replay

6. **Rate Limiting per Webhook**
   - Current: Global rate limit
   - Future: Per-webhook quota

---

## 📖 References

- [Stripe Webhooks Documentation](https://stripe.com/docs/webhooks)
- [GitHub Webhooks Documentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [HMAC: Keyed-Hashing for Message Authentication](https://tools.ietf.org/html/rfc2104)
- [REST API Best Practices](https://restfulapi.net/)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

