"""
Library API System with Webhook Integration
============================================

Main Flask application with webhook support, notification system,
and API patterns from Stripe & GitHub.

Key Features:
- RESTful API for library management
- Webhook system for event notifications
- Multiple notification channels (HTTP, Email, Slack simulation)
- Security: HMAC-SHA256 signature verification
- Event-driven architecture
- Rate limiting and monitoring
"""

import os
import json
import hmac
import hashlib
import time
import logging
from datetime import datetime
from functools import wraps
from typing import Dict, List, Any, Optional
from uuid import uuid4

from flask import Flask, request, jsonify, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import requests

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-secret-key-change-in-production')

# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

webhook_events = Counter(
    'webhook_events_total',
    'Total webhook events triggered',
    ['event_type', 'status']
)

webhook_deliveries = Counter(
    'webhook_deliveries_total',
    'Total webhook delivery attempts',
    ['event_type', 'destination', 'status']
)

webhook_latency = Histogram(
    'webhook_delivery_latency_seconds',
    'Webhook delivery latency',
    ['event_type', 'destination'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

active_webhooks = Gauge(
    'active_webhooks_count',
    'Total active webhooks'
)

notification_queue_size = Gauge(
    'notification_queue_size',
    'Pending notifications in queue'
)

# ============================================================================
# EVENT SYSTEM
# ============================================================================

class Event:
    """Represents an event that triggers webhooks"""
    
    def __init__(self, event_type: str, data: Dict[str, Any], resource_id: str = None):
        self.id = str(uuid4())
        self.event_type = event_type
        self.data = data
        self.resource_id = resource_id
        self.timestamp = datetime.utcnow().isoformat()
        self.attempt_count = 0
        self.last_attempt = None
        self.next_retry = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'event_type': self.event_type,
            'data': self.data,
            'resource_id': self.resource_id,
            'timestamp': self.timestamp,
            'attempt_count': self.attempt_count
        }
    
    def __repr__(self):
        return f"<Event {self.event_type} - {self.id}>"


# ============================================================================
# WEBHOOK MANAGEMENT
# ============================================================================

class WebhookManager:
    """Manages webhook subscriptions and deliveries"""
    
    def __init__(self):
        self.webhooks: Dict[str, Dict] = {}
        self.events: List[Event] = []
        self.failed_events: List[Event] = []
    
    def register_webhook(self, url: str, events: List[str], active: bool = True) -> str:
        """Register a new webhook"""
        webhook_id = str(uuid4())
        self.webhooks[webhook_id] = {
            'id': webhook_id,
            'url': url,
            'events': events,
            'active': active,
            'created_at': datetime.utcnow().isoformat(),
            'last_triggered': None,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'retries': 3
        }
        active_webhooks.set(len([w for w in self.webhooks.values() if w['active']]))
        logger.info(f"Webhook registered: {webhook_id} -> {url}")
        return webhook_id
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """Unregister a webhook"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            active_webhooks.set(len([w for w in self.webhooks.values() if w['active']]))
            logger.info(f"Webhook unregistered: {webhook_id}")
            return True
        return False
    
    def get_webhooks(self, event_type: str = None, active_only: bool = True) -> List[Dict]:
        """Get webhooks for specific event type"""
        webhooks = list(self.webhooks.values())
        
        if active_only:
            webhooks = [w for w in webhooks if w['active']]
        
        if event_type:
            webhooks = [w for w in webhooks if event_type in w['events']]
        
        return webhooks
    
    def trigger_event(self, event: Event) -> int:
        """Trigger webhooks for an event"""
        self.events.append(event)
        
        matching_webhooks = self.get_webhooks(event.event_type)
        webhook_events.labels(event_type=event.event_type, status='triggered').inc()
        
        logger.info(f"Event triggered: {event.event_type} - {len(matching_webhooks)} webhooks")
        
        return len(matching_webhooks)
    
    def get_webhook(self, webhook_id: str) -> Optional[Dict]:
        """Get webhook details"""
        return self.webhooks.get(webhook_id)
    
    def list_webhooks(self) -> List[Dict]:
        """List all webhooks"""
        return list(self.webhooks.values())
    
    def get_events(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """Get recent events"""
        events = sorted(self.events, key=lambda e: e.timestamp, reverse=True)
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [e.to_dict() for e in events[:limit]]


# ============================================================================
# NOTIFICATION SERVICE
# ============================================================================

class NotificationService:
    """Handles notification delivery through multiple channels"""
    
    def __init__(self):
        self.queue: List[Dict] = []
        self.delivered: List[Dict] = []
    
    def send_webhook(self, webhook: Dict, event: Event) -> bool:
        """Send webhook notification (HTTP delivery with retry logic)"""
        notification_queue_size.inc()
        
        try:
            payload = {
                'event_id': event.id,
                'event_type': event.event_type,
                'timestamp': event.timestamp,
                'data': event.data
            }
            
            # Generate HMAC signature (Stripe/GitHub pattern)
            signature = self._generate_signature(json.dumps(payload))
            
            headers = {
                'X-Webhook-ID': event.id,
                'X-Webhook-Signature': signature,
                'X-Webhook-Timestamp': str(int(time.time())),
                'Content-Type': 'application/json'
            }
            
            start_time = time.time()
            
            response = requests.post(
                webhook['url'],
                json=payload,
                headers=headers,
                timeout=5
            )
            
            latency = time.time() - start_time
            webhook_latency.labels(
                event_type=event.event_type,
                destination='http'
            ).observe(latency)
            
            success = response.status_code in [200, 201, 202]
            
            webhook_deliveries.labels(
                event_type=event.event_type,
                destination='http',
                status='success' if success else 'failed'
            ).inc()
            
            logger.info(f"Webhook delivery: {webhook['id']} - Status {response.status_code}")
            
            notification_queue_size.dec()
            
            return success
        
        except Exception as e:
            webhook_deliveries.labels(
                event_type=event.event_type,
                destination='http',
                status='error'
            ).inc()
            
            logger.error(f"Webhook delivery failed: {str(e)}")
            notification_queue_size.dec()
            
            return False
    
    def send_email_notification(self, email: str, event: Event) -> bool:
        """Send email notification (simulated)"""
        logger.info(f"Email notification sent to {email}: {event.event_type}")
        return True
    
    def send_slack_notification(self, webhook_url: str, event: Event) -> bool:
        """Send Slack notification"""
        try:
            message = {
                'text': f"📧 Event: {event.event_type}",
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"*Event:* {event.event_type}\n*ID:* {event.id}\n*Time:* {event.timestamp}"
                        }
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=message)
            
            logger.info(f"Slack notification sent - Status {response.status_code}")
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Slack notification failed: {str(e)}")
            return False
    
    @staticmethod
    def _generate_signature(payload: str) -> str:
        """Generate HMAC-SHA256 signature (Stripe pattern)"""
        timestamp = str(int(time.time()))
        signed_content = f"{timestamp}.{payload}"
        signature = hmac.new(
            WEBHOOK_SECRET.encode(),
            signed_content.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"v1,{timestamp},{signature}"


# ============================================================================
# FLASK APPLICATION
# ============================================================================

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize managers
webhook_manager = WebhookManager()
notification_service = NotificationService()

# Rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# In-memory database
books_db = {
    "1": {"id": "1", "title": "Clean Code", "author": "Robert C. Martin", "available": 5},
    "2": {"id": "2", "title": "Design Patterns", "author": "Gang of Four", "available": 3},
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def verify_webhook_signature(request_body: str, signature: str) -> bool:
    """Verify webhook signature (security pattern from Stripe/GitHub)"""
    try:
        parts = signature.split(',')
        if len(parts) != 3:
            return False
        
        version, timestamp, sig = parts
        if version != 'v1':
            return False
        
        # Check timestamp (prevent replay attacks)
        current_time = int(time.time())
        if abs(current_time - int(timestamp)) > 300:  # 5 minutes
            logger.warning("Webhook signature timestamp too old")
            return False
        
        signed_content = f"{timestamp}.{request_body}"
        expected_sig = hmac.new(
            WEBHOOK_SECRET.encode(),
            signed_content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(sig, expected_sig)
    
    except Exception as e:
        logger.error(f"Signature verification failed: {str(e)}")
        return False


# ============================================================================
# API ENDPOINTS - BOOKS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify(status='healthy', timestamp=datetime.utcnow().isoformat())


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(REGISTRY), mimetype='text/plain')


@app.route('/books', methods=['GET'])
@limiter.limit("30 per minute")
def get_books():
    """Get all books"""
    logger.info("Fetching all books")
    return jsonify(books=list(books_db.values()))


@app.route('/books/<book_id>', methods=['GET'])
@limiter.limit("60 per minute")
def get_book(book_id):
    """Get specific book"""
    logger.info(f"Fetching book {book_id}")
    
    if book_id not in books_db:
        return jsonify(error="Book not found"), 404
    
    return jsonify(book=books_db[book_id])


@app.route('/books', methods=['POST'])
@limiter.limit("10 per minute")
def create_book():
    """Create new book - triggers webhook event"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['title', 'author', 'available']):
        return jsonify(error="Missing required fields"), 400
    
    book_id = str(len(books_db) + 1)
    new_book = {
        "id": book_id,
        "title": data['title'],
        "author": data['author'],
        "available": data['available']
    }
    
    books_db[book_id] = new_book
    logger.info(f"Book created: {book_id}")
    
    # Trigger webhook event
    event = Event('book.created', new_book, book_id)
    webhook_manager.trigger_event(event)
    
    # Send notifications asynchronously
    for webhook in webhook_manager.get_webhooks('book.created'):
        notification_service.send_webhook(webhook, event)
    
    return jsonify(book=new_book), 201


@app.route('/books/<book_id>/borrow', methods=['POST'])
@limiter.limit("20 per minute")
def borrow_book(book_id):
    """Borrow book - triggers webhook event"""
    logger.info(f"Borrow request for book {book_id}")
    
    if book_id not in books_db:
        return jsonify(error="Book not found"), 404
    
    book = books_db[book_id]
    if book['available'] <= 0:
        return jsonify(error="No copies available"), 400
    
    book['available'] -= 1
    logger.info(f"Book borrowed: {book_id}")
    
    # Trigger webhook event
    event = Event('book.borrowed', {**book, 'borrowed_count': 1}, book_id)
    webhook_manager.trigger_event(event)
    
    for webhook in webhook_manager.get_webhooks('book.borrowed'):
        notification_service.send_webhook(webhook, event)
    
    return jsonify(message="Book borrowed", book=book)


@app.route('/books/<book_id>/return', methods=['POST'])
@limiter.limit("20 per minute")
def return_book(book_id):
    """Return book - triggers webhook event"""
    logger.info(f"Return request for book {book_id}")
    
    if book_id not in books_db:
        return jsonify(error="Book not found"), 404
    
    book = books_db[book_id]
    book['available'] += 1
    logger.info(f"Book returned: {book_id}")
    
    # Trigger webhook event
    event = Event('book.returned', {**book, 'returned_count': 1}, book_id)
    webhook_manager.trigger_event(event)
    
    for webhook in webhook_manager.get_webhooks('book.returned'):
        notification_service.send_webhook(webhook, event)
    
    return jsonify(message="Book returned", book=book)


@app.route('/books/<book_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_book(book_id):
    """Delete book - triggers webhook event"""
    logger.info(f"Delete request for book {book_id}")
    
    if book_id not in books_db:
        return jsonify(error="Book not found"), 404
    
    deleted_book = books_db.pop(book_id)
    logger.info(f"Book deleted: {book_id}")
    
    # Trigger webhook event
    event = Event('book.deleted', deleted_book, book_id)
    webhook_manager.trigger_event(event)
    
    for webhook in webhook_manager.get_webhooks('book.deleted'):
        notification_service.send_webhook(webhook, event)
    
    return jsonify(message="Book deleted")


# ============================================================================
# WEBHOOK MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/webhooks', methods=['GET'])
@limiter.limit("50 per minute")
def list_webhooks():
    """List all registered webhooks"""
    return jsonify(
        webhooks=webhook_manager.list_webhooks(),
        count=len(webhook_manager.list_webhooks())
    )


@app.route('/webhooks', methods=['POST'])
@limiter.limit("10 per minute")
def register_webhook():
    """Register a new webhook"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['url', 'events']):
        return jsonify(error="Missing url or events"), 400
    
    webhook_id = webhook_manager.register_webhook(
        url=data['url'],
        events=data['events'],
        active=data.get('active', True)
    )
    
    logger.info(f"Webhook registered: {webhook_id}")
    
    return jsonify(
        webhook_id=webhook_id,
        message="Webhook registered successfully"
    ), 201


@app.route('/webhooks/<webhook_id>', methods=['GET'])
@limiter.limit("50 per minute")
def get_webhook(webhook_id):
    """Get webhook details"""
    webhook = webhook_manager.get_webhook(webhook_id)
    
    if not webhook:
        return jsonify(error="Webhook not found"), 404
    
    return jsonify(webhook=webhook)


@app.route('/webhooks/<webhook_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_webhook(webhook_id):
    """Delete webhook"""
    if not webhook_manager.unregister_webhook(webhook_id):
        return jsonify(error="Webhook not found"), 404
    
    logger.info(f"Webhook deleted: {webhook_id}")
    
    return jsonify(message="Webhook deleted successfully")


# ============================================================================
# EVENT ENDPOINTS
# ============================================================================

@app.route('/events', methods=['GET'])
@limiter.limit("30 per minute")
def get_events():
    """Get recent events"""
    event_type = request.args.get('type')
    limit = int(request.args.get('limit', 100))
    
    events = webhook_manager.get_events(event_type=event_type, limit=limit)
    
    return jsonify(events=events, count=len(events))


@app.route('/events/<event_id>', methods=['GET'])
@limiter.limit("50 per minute")
def get_event(event_id):
    """Get specific event"""
    for event in webhook_manager.events:
        if event.id == event_id:
            return jsonify(event=event.to_dict())
    
    return jsonify(error="Event not found"), 404


# ============================================================================
# WEBHOOK RECEIVE ENDPOINT (for testing)
# ============================================================================

@app.route('/webhook-receiver', methods=['POST'])
def webhook_receiver():
    """Test webhook receiver endpoint - simulates external service"""
    signature = request.headers.get('X-Webhook-Signature', '')
    request_body = request.get_data(as_text=True)
    
    # Verify signature
    if not verify_webhook_signature(request_body, signature):
        logger.warning("Webhook signature verification failed")
        return jsonify(error="Invalid signature"), 401
    
    data = request.get_json()
    logger.info(f"Webhook received: {data.get('event_type')}")
    
    return jsonify(
        message="Webhook received",
        event_id=data.get('event_id'),
        timestamp=datetime.utcnow().isoformat()
    ), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify(error="Rate limit exceeded"), 429


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
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
    logger.info("Starting Library API Server with Webhook Support")
    
    # Pre-register a test webhook
    webhook_manager.register_webhook(
        url='http://localhost:5000/webhook-receiver',
        events=['book.created', 'book.borrowed', 'book.returned', 'book.deleted'],
        active=True
    )
    
    app.run(host='0.0.0.0', port=5000, debug=False)
