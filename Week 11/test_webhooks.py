"""
Comprehensive Test Suite for Webhook Integration
Tests all webhook functionality, security, and delivery
"""

import requests
import json
import time
import hmac
import hashlib
from datetime import datetime

BASE_URL = "http://localhost:5000"
WEBHOOK_SECRET = "your-secret-key-change-in-production"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(title):
    """Print section header"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Colors.END}\n")

def print_success(msg):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    """Print error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_test(test_num, name):
    """Print test name"""
    print(f"\nTest {test_num}: {name}")
    print("-" * 50)

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_health_check():
    """Test 1: Health check endpoint"""
    print_test(1, "Health Check")
    
    try:
        resp = requests.get(f"{BASE_URL}/health")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'healthy':
                print_success(f"Health check passed")
                return True
            else:
                print_error(f"Unexpected status: {data.get('status')}")
                return False
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_register_webhook():
    """Test 2: Register webhook"""
    print_test(2, "Register Webhook")
    
    try:
        payload = {
            "url": "http://localhost:5000/webhook-receiver",
            "events": ["book.created", "book.borrowed"],
            "active": True
        }
        
        resp = requests.post(f"{BASE_URL}/webhooks", json=payload)
        
        if resp.status_code == 201:
            data = resp.json()
            webhook_id = data.get('webhook_id')
            print_success(f"Webhook registered: {webhook_id}")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return webhook_id
        else:
            print_error(f"Status code: {resp.status_code}")
            print_error(f"Response: {resp.text}")
            return None
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None


def test_list_webhooks():
    """Test 3: List webhooks"""
    print_test(3, "List Webhooks")
    
    try:
        resp = requests.get(f"{BASE_URL}/webhooks")
        
        if resp.status_code == 200:
            data = resp.json()
            count = data.get('count', 0)
            print_success(f"Found {count} webhooks")
            
            for webhook in data.get('webhooks', [])[:3]:
                print_info(f"  ID: {webhook['id'][:8]}... | URL: {webhook['url']} | Events: {webhook['events']}")
            
            return True
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_get_webhook(webhook_id):
    """Test 4: Get specific webhook"""
    print_test(4, "Get Webhook Details")
    
    if not webhook_id:
        print_error("No webhook ID provided")
        return False
    
    try:
        resp = requests.get(f"{BASE_URL}/webhooks/{webhook_id}")
        
        if resp.status_code == 200:
            data = resp.json()
            webhook = data.get('webhook', {})
            print_success(f"Webhook retrieved: {webhook.get('id')[:8]}...")
            print_info(f"  URL: {webhook.get('url')}")
            print_info(f"  Active: {webhook.get('active')}")
            print_info(f"  Events: {webhook.get('events')}")
            print_info(f"  Successful deliveries: {webhook.get('successful_deliveries')}")
            print_info(f"  Failed deliveries: {webhook.get('failed_deliveries')}")
            return True
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_create_book():
    """Test 5: Create book (triggers webhook)"""
    print_test(5, "Create Book (Triggers Webhook)")
    
    try:
        payload = {
            "title": "Python Advanced",
            "author": "Mark Lutz",
            "available": 3
        }
        
        resp = requests.post(f"{BASE_URL}/books", json=payload)
        
        if resp.status_code == 201:
            data = resp.json()
            book = data.get('book', {})
            book_id = book.get('id')
            print_success(f"Book created: {book_id} - {book.get('title')}")
            print_info(f"Event 'book.created' should be triggered")
            return book_id
        else:
            print_error(f"Status code: {resp.status_code}")
            return None
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None


def test_get_events():
    """Test 6: Get recent events"""
    print_test(6, "Get Events")
    
    try:
        resp = requests.get(f"{BASE_URL}/events?limit=10")
        
        if resp.status_code == 200:
            data = resp.json()
            count = data.get('count', 0)
            print_success(f"Retrieved {count} events")
            
            for event in data.get('events', [])[:3]:
                print_info(f"  Type: {event['event_type']} | ID: {event['id'][:8]}... | Time: {event['timestamp']}")
            
            return True
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_get_event_by_type():
    """Test 7: Get events by type"""
    print_test(7, "Get Events by Type")
    
    try:
        resp = requests.get(f"{BASE_URL}/events?type=book.created&limit=5")
        
        if resp.status_code == 200:
            data = resp.json()
            events = data.get('events', [])
            
            # Check if all events are of correct type
            correct_type = all(e['event_type'] == 'book.created' for e in events)
            
            if correct_type:
                print_success(f"Retrieved {len(events)} 'book.created' events")
                return True
            else:
                print_error("Events contain incorrect types")
                return False
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_get_specific_event(event_id=None):
    """Test 8: Get specific event"""
    print_test(8, "Get Specific Event")
    
    try:
        # Get a recent event first
        resp = requests.get(f"{BASE_URL}/events?limit=1")
        
        if resp.status_code != 200:
            print_error("Could not retrieve events list")
            return False
        
        events = resp.json().get('events', [])
        
        if not events:
            print_error("No events available")
            return False
        
        event_id = events[0]['id']
        
        # Now get specific event
        resp = requests.get(f"{BASE_URL}/events/{event_id}")
        
        if resp.status_code == 200:
            data = resp.json()
            event = data.get('event', {})
            print_success(f"Event retrieved: {event.get('event_type')}")
            print_info(f"  ID: {event.get('id')}")
            print_info(f"  Timestamp: {event.get('timestamp')}")
            print_info(f"  Data: {json.dumps(event.get('data'), indent=4)[:100]}...")
            return True
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_borrow_book():
    """Test 9: Borrow book (triggers webhook)"""
    print_test(9, "Borrow Book (Triggers Webhook)")
    
    try:
        # Get available book
        resp = requests.get(f"{BASE_URL}/books")
        if resp.status_code != 200 or not resp.json().get('books'):
            print_error("No books available")
            return False
        
        book_id = resp.json()['books'][0]['id']
        
        # Borrow book
        resp = requests.post(f"{BASE_URL}/books/{book_id}/borrow")
        
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"Book borrowed: {book_id}")
            print_info(f"Event 'book.borrowed' should be triggered")
            print_info(f"Available copies: {data['book']['available']}")
            return True
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_return_book():
    """Test 10: Return book (triggers webhook)"""
    print_test(10, "Return Book (Triggers Webhook)")
    
    try:
        resp = requests.get(f"{BASE_URL}/books")
        if resp.status_code != 200 or not resp.json().get('books'):
            print_error("No books available")
            return False
        
        book_id = resp.json()['books'][0]['id']
        
        resp = requests.post(f"{BASE_URL}/books/{book_id}/return")
        
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"Book returned: {book_id}")
            print_info(f"Event 'book.returned' should be triggered")
            print_info(f"Available copies: {data['book']['available']}")
            return True
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_webhook_receiver():
    """Test 11: Webhook receiver (verify signature)"""
    print_test(11, "Webhook Receiver - Signature Verification")
    
    try:
        payload = {
            "event_id": "test-event-id",
            "event_type": "test.event",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"test": "data"}
        }
        
        payload_json = json.dumps(payload)
        timestamp = str(int(time.time()))
        signed_content = f"{timestamp}.{payload_json}"
        signature = hmac.new(
            WEBHOOK_SECRET.encode(),
            signed_content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'X-Webhook-Signature': f"v1,{timestamp},{signature}",
            'Content-Type': 'application/json'
        }
        
        resp = requests.post(
            f"{BASE_URL}/webhook-receiver",
            json=payload,
            headers=headers
        )
        
        if resp.status_code == 200:
            print_success("Webhook received and verified successfully")
            return True
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_invalid_signature():
    """Test 12: Invalid signature rejection"""
    print_test(12, "Invalid Signature Rejection")
    
    try:
        payload = {
            "event_id": "test-event-id",
            "event_type": "test.event",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"test": "data"}
        }
        
        payload_json = json.dumps(payload)
        
        # Use wrong signature
        headers = {
            'X-Webhook-Signature': "v1,1234567890,invalidsignature",
            'Content-Type': 'application/json'
        }
        
        resp = requests.post(
            f"{BASE_URL}/webhook-receiver",
            json=payload,
            headers=headers
        )
        
        if resp.status_code == 401:
            print_success("Invalid signature correctly rejected (401)")
            return True
        else:
            print_error(f"Expected 401, got {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_metrics_endpoint():
    """Test 13: Prometheus metrics"""
    print_test(13, "Prometheus Metrics")
    
    try:
        resp = requests.get(f"{BASE_URL}/metrics")
        
        if resp.status_code == 200:
            metrics = resp.text
            
            # Check for key metrics
            has_webhook_metrics = (
                'webhook_events_total' in metrics and
                'webhook_deliveries_total' in metrics and
                'webhook_delivery_latency_seconds' in metrics
            )
            
            if has_webhook_metrics:
                print_success("Prometheus metrics available")
                print_info(f"  Metrics size: {len(metrics)} bytes")
                print_info(f"  Contains webhook metrics: webhook_events, webhook_deliveries, webhook_latency")
                return True
            else:
                print_error("Webhook metrics not found")
                return False
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_delete_webhook(webhook_id):
    """Test 14: Delete webhook"""
    print_test(14, "Delete Webhook")
    
    if not webhook_id:
        print_error("No webhook ID provided")
        return False
    
    try:
        resp = requests.delete(f"{BASE_URL}/webhooks/{webhook_id}")
        
        if resp.status_code == 200:
            print_success(f"Webhook deleted: {webhook_id}")
            return True
        else:
            print_error(f"Status code: {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_rate_limiting():
    """Test 15: Rate limiting"""
    print_test(15, "Rate Limiting")
    
    try:
        print_info("Making 31 rapid requests to /books (limit: 30/min)...")
        
        success_count = 0
        rate_limited = 0
        
        for i in range(31):
            resp = requests.get(f"{BASE_URL}/books")
            
            if resp.status_code == 200:
                success_count += 1
            elif resp.status_code == 429:
                rate_limited += 1
        
        if rate_limited > 0:
            print_success(f"Rate limiting working: {success_count} success, {rate_limited} rate limited")
            return True
        else:
            print_error(f"Rate limiting not triggered (all {success_count} succeeded)")
            return False
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "WEBHOOK INTEGRATION TEST SUITE" + " "*24 + "║")
    print("║" + f" Server: {BASE_URL}".ljust(69) + "║")
    print("║" + f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(69) + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.END}\n")
    
    results = []
    webhook_id = None
    
    # Run tests
    tests = [
        (1, "Health Check", lambda: test_health_check()),
        (2, "Register Webhook", lambda: test_register_webhook()),
        (3, "List Webhooks", lambda: test_list_webhooks()),
        (4, "Get Webhook Details", lambda: test_get_webhook(webhook_id)),
        (5, "Create Book", lambda: test_create_book()),
        (6, "Get Events", lambda: test_get_events()),
        (7, "Get Events by Type", lambda: test_get_events_by_type()),
        (8, "Get Specific Event", lambda: test_get_specific_event()),
        (9, "Borrow Book", lambda: test_borrow_book()),
        (10, "Return Book", lambda: test_return_book()),
        (11, "Webhook Receiver", lambda: test_webhook_receiver()),
        (12, "Invalid Signature", lambda: test_invalid_signature()),
        (13, "Prometheus Metrics", lambda: test_metrics_endpoint()),
        (14, "Delete Webhook", lambda: test_delete_webhook(webhook_id)),
        (15, "Rate Limiting", lambda: test_rate_limiting()),
    ]
    
    for test_num, test_name, test_func in tests:
        result = test_func()
        
        if test_num == 2 and result:  # Capture webhook_id from register test
            webhook_id = result
            result = True
        
        results.append((test_name, "PASS" if result else "FAIL"))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    print(f"{'Test Name':<35} | {'Result':<10}")
    print("-" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result == "PASS":
            print(f"{Colors.GREEN}{test_name:<35} | {result:<10}{Colors.END}")
            passed += 1
        else:
            print(f"{Colors.RED}{test_name:<35} | {result:<10}{Colors.END}")
            failed += 1
    
    print("-" * 50)
    print(f"Total: {passed + failed} tests")
    
    print(f"\n{Colors.GREEN}✓ Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}✗ Failed: {failed}{Colors.END}")
    
    success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
    print(f"\n{Colors.BLUE}Success Rate: {success_rate:.1f}%{Colors.END}")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        print_info("Make sure Flask app is running:")
        print_info("  python app.py")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
