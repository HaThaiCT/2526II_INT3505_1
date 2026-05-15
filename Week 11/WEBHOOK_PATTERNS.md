# Webhook Implementation Patterns & Best Practices

Hướng dẫn chi tiết về các patterns webhook, security, và best practices.

## 📋 Table of Contents

1. [Webhook Fundamentals](#webhook-fundamentals)
2. [Security Patterns](#security-patterns)
3. [Event Management](#event-management)
4. [Retry Strategies](#retry-strategies)
5. [Error Handling](#error-handling)
6. [Best Practices](#best-practices)
7. [Common Pitfalls](#common-pitfalls)

---

## 🔌 Webhook Fundamentals

### What is a Webhook?

A webhook is an HTTP callback mechanism that allows services to send real-time notifications about events.

```
Your Service                External Service
    |                             |
    |-- Event Occurs              |
    |                             |
    +---> Generate Event -------> |
          |                       |
          +-- HTTP POST --------> Process Notification
                                  |
                                  Return 200 OK
```

### Webhook vs Polling

| Aspect | Webhook | Polling |
|--------|---------|---------|
| **Latency** | Immediate | Delayed (seconds to minutes) |
| **Load** | Event-driven | Constant |
| **Complexity** | Higher (needs signature verification) | Lower |
| **Scalability** | Better | Worse |
| **Real-time** | Yes | No |

### When to Use Webhooks

✅ **Use webhooks for:**
- Real-time notifications
- Event-driven systems
- Asynchronous updates
- Third-party integrations

❌ **Don't use webhooks for:**
- One-time queries
- High-frequency updates (1000s/sec)
- When client can poll efficiently
- Simple request-response interactions

---

## 🔐 Security Patterns

### 1. HMAC-SHA256 Signature Pattern

**Why HMAC?**
- Proves message authenticity
- Prevents tampering
- Verifies sender identity
- Industry standard (Stripe, GitHub, etc.)

**Implementation:**

```python
import hmac
import hashlib
import time

WEBHOOK_SECRET = "shared-secret-key"

# SENDING SIDE (Your API)
def send_webhook(url, payload):
    timestamp = str(int(time.time()))
    payload_json = json.dumps(payload)
    signed_content = f"{timestamp}.{payload_json}"
    
    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        signed_content.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'X-Webhook-Signature': f"v1,{timestamp},{signature}"
    }
    
    requests.post(url, json=payload, headers=headers)


# RECEIVING SIDE (Client)
def verify_webhook(request_body, signature_header):
    parts = signature_header.split(',')
    version, timestamp, signature = parts
    
    # Verify timestamp (prevent replay)
    if abs(int(time.time()) - int(timestamp)) > 300:
        return False
    
    # Verify signature
    signed_content = f"{timestamp}.{request_body}"
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        signed_content.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison (prevent timing attack)
    return hmac.compare_digest(signature, expected_signature)
```

### 2. Timestamp Validation (Replay Attack Prevention)

```python
def is_timestamp_valid(timestamp_str, tolerance_seconds=300):
    """
    Verify timestamp is recent (within 5 minutes)
    Prevents replay attacks where attacker resends old webhooks
    """
    try:
        timestamp = int(timestamp_str)
        current_time = int(time.time())
        
        # Allow 5-minute clock skew
        if abs(current_time - timestamp) > tolerance_seconds:
            logger.warning(f"Webhook timestamp too old: {timestamp}")
            return False
        
        return True
    except ValueError:
        return False
```

### 3. IP Whitelisting (Defense-in-Depth)

```python
from flask import request

ALLOWED_IPS = [
    '192.168.1.100',
    '10.0.0.0/8'
]

def is_ip_allowed(request_ip):
    """Check if request IP is in whitelist"""
    # Simple check
    if request_ip in ALLOWED_IPS:
        return True
    
    # CIDR check (if using ipaddress library)
    from ipaddress import ip_address, ip_network
    
    ip = ip_address(request_ip)
    for allowed in ALLOWED_IPS:
        if '/' in allowed:  # CIDR notation
            if ip in ip_network(allowed):
                return True
    
    return False

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    # Check IP
    client_ip = request.remote_addr
    if not is_ip_allowed(client_ip):
        logger.warning(f"Webhook from unauthorized IP: {client_ip}")
        return jsonify(error="Unauthorized"), 403
    
    # Continue with other checks
    ...
```

### 4. Rate Limiting per Webhook

```python
from flask_limiter import Limiter

limiter = Limiter(app=app, key_func=lambda: request.remote_addr)

# Different rates for different webhooks
@app.route('/webhook/payment', methods=['POST'])
@limiter.limit("1000 per hour")
def payment_webhook():
    """High-volume payment updates"""
    ...

@app.route('/webhook/notification', methods=['POST'])
@limiter.limit("100 per hour")
def notification_webhook():
    """Lower-volume notifications"""
    ...
```

---

## 📨 Event Management

### 1. Event Payload Design

```python
class WebhookEvent:
    """Standard webhook event structure"""
    
    def __init__(self, event_type: str, resource: dict):
        self.id = str(uuid4())  # Unique ID for deduplication
        self.event_type = event_type
        self.timestamp = datetime.utcnow().isoformat()
        self.data = resource
        self.api_version = "v1"
    
    def to_json(self) -> dict:
        return {
            'id': self.id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'data': self.data,
            'api_version': self.api_version
        }

# Example payload:
{
    "id": "evt_550e8400-e29b-41d4-a716",
    "event_type": "book.borrowed",
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "data": {
        "id": "1",
        "title": "Clean Code",
        "borrowed_by": "user123",
        "borrowed_at": "2024-01-15T10:30:45Z"
    },
    "api_version": "v1"
}
```

### 2. Event Versioning

```python
# Keep backward compatibility while adding new fields

# Event V1 (old)
event_v1 = {
    "event_type": "book.created",
    "data": {"id": "1", "title": "Book"}
}

# Event V2 (new, backward compatible)
event_v2 = {
    "id": "evt_...",  # NEW
    "event_type": "book.created",
    "timestamp": "2024-01-15T...",  # NEW
    "data": {"id": "1", "title": "Book"},
    "api_version": "v1"  # NEW
}

# V2 still works with V1 clients (ignores new fields)
# V2 allows V2 clients to use new features
```

### 3. Event Filtering

```python
# Allow subscribers to filter events

def register_webhook(url: str, event_filters: dict):
    """
    event_filters = {
        'event_types': ['book.created', 'book.borrowed'],
        'resource_id': '123',  # Optional
        'status': ['completed']  # Optional
    }
    """
    webhook = {
        'url': url,
        'filters': event_filters,
        'created_at': datetime.now()
    }
    save_webhook(webhook)


def should_deliver_event(event: Event, webhook: dict) -> bool:
    """Check if event matches webhook filters"""
    filters = webhook['filters']
    
    # Check event type
    if event.event_type not in filters['event_types']:
        return False
    
    # Check resource ID (if specified)
    if 'resource_id' in filters:
        if event.resource_id != filters['resource_id']:
            return False
    
    # Check status (if specified)
    if 'status' in filters:
        if event.data.get('status') not in filters['status']:
            return False
    
    return True
```

---

## 🔄 Retry Strategies

### 1. Exponential Backoff Pattern

```python
import time
from datetime import datetime, timedelta

class RetryScheduler:
    """Schedule retries with exponential backoff"""
    
    # Configuration
    MAX_RETRIES = 5
    INITIAL_DELAY = 5  # seconds
    BACKOFF_MULTIPLIER = 2
    MAX_DELAY = 3600  # 1 hour max
    
    @staticmethod
    def calculate_retry_delay(attempt_number: int) -> int:
        """Calculate delay for next retry"""
        delay = RetryScheduler.INITIAL_DELAY * (
            RetryScheduler.BACKOFF_MULTIPLIER ** attempt_number
        )
        # Cap maximum delay
        return min(int(delay), RetryScheduler.MAX_DELAY)
    
    @staticmethod
    def should_retry(attempt: int) -> bool:
        """Check if should retry"""
        return attempt < RetryScheduler.MAX_RETRIES
    
    @staticmethod
    def get_next_retry_time(attempt: int) -> datetime:
        """Get next retry time"""
        delay = RetryScheduler.calculate_retry_delay(attempt)
        return datetime.now() + timedelta(seconds=delay)

# Usage:
attempt = 0
while RetryScheduler.should_retry(attempt):
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code in [200, 201, 202]:
            return True  # Success
    except Exception as e:
        logger.error(f"Attempt {attempt}: {str(e)}")
    
    if RetryScheduler.should_retry(attempt):
        next_retry = RetryScheduler.get_next_retry_time(attempt)
        time.sleep((next_retry - datetime.now()).total_seconds())
        attempt += 1

logger.error("All retry attempts failed")
return False
```

### 2. Retry Schedule Visualization

```
Attempt 1: Immediate
Attempt 2: 5 seconds later
Attempt 3: 10 seconds later (5 * 2)
Attempt 4: 20 seconds later (10 * 2)
Attempt 5: 40 seconds later (20 * 2)

Total retry window: ~75 seconds
If configured to retry over 24 hours: up to 10+ retries
```

### 3. Dead Letter Queue Pattern

```python
from collections import deque

class DeadLetterQueue:
    """Store failed webhook deliveries for later analysis"""
    
    def __init__(self, max_size=1000):
        self.queue = deque(maxlen=max_size)
    
    def add(self, webhook_id: str, event: dict, error: str):
        """Add failed delivery to queue"""
        self.queue.append({
            'webhook_id': webhook_id,
            'event': event,
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'retry_count': 0
        })
    
    def get_retry_candidates(self) -> list:
        """Get items ready for retry"""
        candidates = []
        for item in self.queue:
            if item['retry_count'] < 3:
                candidates.append(item)
        return candidates
    
    def replay_event(self, item_id: int):
        """Replay a failed event"""
        for item in self.queue:
            if item.get('id') == item_id:
                item['retry_count'] += 1
                # Re-attempt delivery
                return True
        return False

# Usage:
dlq = DeadLetterQueue()

try:
    send_webhook(webhook, event)
except Exception as e:
    dlq.add(webhook['id'], event, str(e))
```

---

## ❌ Error Handling

### 1. HTTP Status Code Decision Tree

```
Response Code Decision:

200-202 Success ✓ Done
├─ No retry
└─ Mark as successful

3xx Redirect ? Evaluate
├─ Follow redirect (1 time)
└─ Retry if still not 2xx

4xx Client Error ✗ Don't retry
├─ 400 Bad Request → Fix and resend
├─ 401 Unauthorized → Check credentials
├─ 403 Forbidden → Check permissions
├─ 404 Not Found → Remove/fix endpoint
└─ 429 Rate Limited → Retry later

5xx Server Error → Retry
├─ 500 Internal Error
├─ 502 Bad Gateway
├─ 503 Service Unavailable
└─ 504 Gateway Timeout

Timeout → Retry
└─ Network issue

Connection Error → Retry
└─ Network connectivity
```

### 2. Error Handling Implementation

```python
def send_webhook_with_retry(webhook: dict, event: dict) -> bool:
    """Send webhook with proper error handling"""
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                webhook['url'],
                json=event,
                timeout=5
            )
            
            # Success
            if response.status_code in [200, 201, 202]:
                logger.info(f"Webhook delivered: {webhook['id']}")
                return True
            
            # Client error (don't retry)
            elif 400 <= response.status_code < 500:
                logger.error(
                    f"Client error {response.status_code}: {webhook['url']}"
                )
                return False
            
            # Server error (retry)
            elif response.status_code >= 500:
                logger.warning(
                    f"Server error {response.status_code}, retrying..."
                )
                # Continue to retry logic
            
            # Other (retry)
            else:
                logger.warning(f"Unexpected status {response.status_code}")
        
        except requests.Timeout:
            logger.warning(f"Timeout, retrying... (attempt {attempt + 1})")
        
        except requests.ConnectionError:
            logger.warning(f"Connection error, retrying... (attempt {attempt + 1})")
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False
        
        # Wait before retry (exponential backoff)
        if attempt < MAX_RETRIES - 1:
            delay = INITIAL_DELAY * (2 ** attempt)
            time.sleep(delay)
    
    # All retries failed
    logger.error(f"Webhook delivery failed after {MAX_RETRIES} attempts")
    return False
```

---

## ✅ Best Practices

### 1. **Always Verify Signatures**

```python
# BAD ❌
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    # Process without checking signature!
    data = request.get_json()
    process_event(data)

# GOOD ✅
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    signature = request.headers.get('X-Webhook-Signature')
    body = request.get_data(as_text=True)
    
    if not verify_signature(body, signature):
        logger.error("Signature verification failed")
        return 401
    
    data = request.get_json()
    process_event(data)
```

### 2. **Make Processing Idempotent**

```python
# BAD ❌
def process_event(event):
    # Process every time (duplicates if retried)
    user.balance -= 100
    transaction.save()

# GOOD ✅
def process_event(event):
    # Check if already processed
    if already_processed(event['id']):
        return
    
    # Process only once
    user.balance -= 100
    transaction.save()
    
    # Mark as processed
    mark_processed(event['id'])
```

### 3. **Implement Timeouts**

```python
# BAD ❌
response = requests.post(url, json=payload)
# Hangs forever if server doesn't respond

# GOOD ✅
try:
    response = requests.post(
        url,
        json=payload,
        timeout=5  # 5 second timeout
    )
except requests.Timeout:
    logger.error("Webhook delivery timed out")
    # Retry logic
```

### 4. **Monitor and Alert**

```python
def send_webhook_monitored(webhook: dict, event: dict):
    """Send webhook with monitoring"""
    
    metrics.webhook_attempt_total.inc()
    start_time = time.time()
    
    try:
        response = requests.post(webhook['url'], json=event)
        
        duration = time.time() - start_time
        metrics.webhook_latency.observe(duration)
        
        if response.status_code in [200, 201, 202]:
            metrics.webhook_success_total.inc()
            return True
        else:
            metrics.webhook_failure_total.inc()
            return False
    
    except Exception as e:
        metrics.webhook_error_total.inc()
        logger.error(f"Webhook error: {str(e)}")
        return False
```

### 5. **Provide Debugging Info**

```python
# Good webhook response
{
    "id": "550e8400-e29b-41d4-a716",  # For tracking
    "received_at": "2024-01-15T10:30:45Z",
    "status": "queued",
    "message": "Webhook received and queued for processing"
}

# Include in logs
logger.info(
    f"Webhook received",
    extra={
        'webhook_id': webhook['id'],
        'event_type': event['event_type'],
        'timestamp': datetime.now().isoformat(),
        'client_ip': request.remote_addr
    }
)
```

---

## ⚠️ Common Pitfalls

### 1. **Not Handling Retries Properly**

❌ **Problem:**
```python
# Returns immediately without retry
response = requests.post(url, json=payload)
return response.status_code == 200
```

✅ **Solution:**
```python
# Implements retry with exponential backoff
for attempt in range(3):
    response = requests.post(url, json=payload)
    if response.status_code in [200, 201, 202]:
        return True
    time.sleep(2 ** attempt)
return False
```

### 2. **Ignoring Network Errors**

❌ **Problem:**
```python
response = requests.post(url, json=payload)  # Can throw exception!
```

✅ **Solution:**
```python
try:
    response = requests.post(url, json=payload, timeout=5)
except (requests.Timeout, requests.ConnectionError) as e:
    logger.error(f"Delivery failed: {str(e)}")
    # Handle retry
```

### 3. **Processing Duplicates**

❌ **Problem:**
```python
# Every retry processes same event
webhook_received()
    → deduct_payment()
    → send_email()

# If webhook is delivered twice (retry): deduct twice!
```

✅ **Solution:**
```python
# Check if already processed using event ID
if cache.exists(f"processed:{event_id}"):
    return 200  # Already handled
else:
    process_event()
    cache.set(f"processed:{event_id}", True, ttl=24h)
```

### 4. **Not Validating Signatures**

❌ **Problem:**
```python
# Accept any webhook
data = request.get_json()
process(data)  # What if spoofed?
```

✅ **Solution:**
```python
# Always verify
signature = request.headers.get('X-Webhook-Signature')
if not verify_signature(request.get_data(), signature):
    return 401
```

### 5. **Synchronous Processing**

❌ **Problem:**
```python
# Webhook sender waits for processing
@app.route('/webhook', methods=['POST'])
def webhook():
    process_expensive_operation()  # Takes 30 seconds!
    return 200
```

✅ **Solution:**
```python
# Queue and return immediately
@app.route('/webhook', methods=['POST'])
def webhook():
    queue.enqueue(process_event, event)
    return 202  # Accepted (not yet processed)
```

---

## 📊 Webhook Lifecycle Diagram

```
Event Occurs
    ↓
Create Event Object
    ├─ Unique ID
    ├─ Timestamp
    └─ Data
    ↓
Find Matching Webhooks
    ↓
For Each Webhook:
    ├─ Generate Signature (HMAC-SHA256)
    ├─ Add Headers (X-Webhook-*)
    ├─ Send POST Request
    └─ Handle Response:
        ├─ 200-202: Success ✓
        ├─ 4xx: Error (don't retry)
        ├─ 5xx/Timeout: Retry ↻
        └─ Max retries: → Dead Letter Queue
    ↓
Log Event & Metrics
    ├─ Success count
    ├─ Failure count
    └─ Latency metrics
    ↓
Return to Sender
```

---

## 🎓 Key Takeaways

1. **Security First**: Always verify signatures
2. **Idempotent**: Design for retries and duplicates
3. **Reliable**: Implement retry logic with backoff
4. **Observable**: Log and monitor everything
5. **Efficient**: Return quickly, process asynchronously
6. **Debuggable**: Include tracking IDs and timestamps

---

## 📚 References

- [Webhook Best Practices](https://requestbin.fullstory.com/)
- [OWASP API Security](https://owasp.org/www-project-web-security-testing-guide/)
- [HMAC vs HMAC-SHA256](https://en.wikipedia.org/wiki/HMAC)
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)

